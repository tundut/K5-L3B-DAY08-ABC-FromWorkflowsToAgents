"""B3 verifies all quote facts, bounded repair, safety and adversarial outcomes."""

import json
import time
from copy import deepcopy

import pytest

from bonus import swarm_verified as verified
from lab8.config_loader import repo_path
from lab8.db import connect, init_store, load_json, load_jsonl
from lab8.durability import InjectedCrash
from lab8.metrics import trial_pass
from lab8.schemas import Budget
from lab8.tools import compute_compensation, lookup_order, tool_cost
from tests.conftest import BY_ID


@pytest.fixture(autouse=True)
def isolated_artifacts(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)


@pytest.mark.parametrize("seed", [11, 22, 33, 44, 55])
@pytest.mark.parametrize("claim_id", list(BY_ID))
def test_verified_swarm_passes_public(public_db, claim_id, seed):
    started = time.time()
    result = verified.run_claim(claim_id, seed=seed, store_path=str(public_db))
    conn = connect(public_db)
    try:
        assert trial_pass(result.as_dict(), BY_ID[claim_id]["expected"], conn, started_at=started) == (True, "ok")
    finally:
        conn.close()


@pytest.mark.parametrize("seed", [11, 55])
@pytest.mark.parametrize("claim", load_jsonl(repo_path("bonus", "cases.jsonl")), ids=lambda row: row["scenario"])
def test_manual_adversarial_labels(tmp_path, claim, seed):
    store = tmp_path / "adversarial.sqlite"
    claims = load_jsonl(repo_path("bonus", "cases.jsonl"))
    init_store(store, load_json(repo_path("bonus", "world.json")), claims).close()
    result = verified.run_claim(claim["claim_id"], seed=seed, store_path=str(store))
    conn = connect(store)
    try:
        assert trial_pass(result.as_dict(), claim["expected"], conn) == (True, "ok")
    finally:
        conn.close()


@pytest.mark.parametrize("field,bad", [("delay_days", 0), ("status", "cancelled"),
                                       ("damage_verified", True), ("shipping_fee_vnd", 999999), ("paid_vnd", 1)])
def test_verifier_checks_each_fact_and_repairs_once(public_db, monkeypatch, field, bad):
    conn = connect(public_db)
    try:
        canonical = lookup_order(conn, "O-107", "P-100")["order"]
        expected = compute_compensation(conn, canonical)
        candidate = {**canonical, field: bad}
        calls = []
        real = verified.compute_compensation

        def counted(conn, order):
            calls.append(order)
            return real(conn, order)

        monkeypatch.setattr(verified, "compute_compensation", counted)
        budget = Budget()
        result = verified.verify_quote(conn, budget, candidate, {"amount_vnd": 999999}, order_id="O-107", principal_id="P-100")
        assert result["changed_fields"] == [field]
        assert result["quote"] == expected
        assert len(calls) == 1
        assert budget.tool_calls == 2
        assert budget.cost_estimate == 2 * tool_cost()
    finally:
        conn.close()


def test_matching_facts_do_not_requote(public_db, monkeypatch):
    conn = connect(public_db)
    try:
        order = lookup_order(conn, "O-107", "P-100")["order"]
        quote = compute_compensation(conn, order)
        def unexpected(*args):
            pytest.fail("matching facts must not add a repair")
        monkeypatch.setattr(verified, "compute_compensation", unexpected)
        result = verified.verify_quote(conn, Budget(), order, quote, order_id="O-107", principal_id="P-100")
        assert result["changed_fields"] == []
        assert result["quote"] == quote
    finally:
        conn.close()


def test_verifier_cannot_read_another_principals_order(public_db):
    conn = connect(public_db)
    try:
        result = verified.verify_quote(conn, Budget(), {}, {}, order_id="O-107", principal_id="P-NOT-OWNER")
        assert result == {"visible": False, "reason": "outside_principal_scope"}
    finally:
        conn.close()


def test_override_trace_explains_t02_repair(public_db):
    result = verified.run_claim("C-002", seed=55, store_path=str(public_db))
    with open(result.trace_path, encoding="utf-8") as handle:
        overrides = [e for e in json.load(handle)["events"] if e["kind"] == "verifier_override"]
    assert overrides == [{"kind": "verifier_override", "payload": {
        "changed_fields": ["delay_days"], "previous_amount_vnd": 20000, "corrected_amount_vnd": 0}}]
    assert result.status == "denied"


@pytest.mark.parametrize("point", ["before_effect", "after_effect_before_checkpoint", "after_checkpoint"])
def test_verified_crash_resume_and_top_up(public_db, point):
    with pytest.raises(InjectedCrash):
        verified.run_claim("C-014", seed=55, store_path=str(public_db), crash_at=point)
    verified.run_claim("C-014", seed=55, store_path=str(public_db))
    replay = verified.run_claim("C-014", seed=55, store_path=str(public_db))
    conn = connect(public_db)
    try:
        assert trial_pass(replay.as_dict(), BY_ID["C-014"]["expected"], conn) == (True, "ok")
    finally:
        conn.close()


@pytest.mark.parametrize("approval_id", [None, "A-008"])
def test_verified_swarm_still_requires_own_approval(public_db, approval_id):
    conn = connect(public_db)
    try:
        conn.execute("UPDATE claims SET approval_id=? WHERE claim_id='C-001'", (approval_id,))
        conn.commit()
        result = verified.run_claim("C-001", seed=55, store_path=str(public_db))
        assert result.status == "denied"
        assert result.proposal_amount == 35000
        assert result.refund_effects == []
        assert conn.execute("SELECT COUNT(*) FROM refund_ledger WHERE claim_id='C-001'").fetchone()[0] == 0
    finally:
        conn.close()


@pytest.mark.parametrize("field,bad", [("delay_days", 0), ("status", "cancelled"), ("damage_verified", True)])
def test_full_shape_repairs_corrupted_worker_facts_before_any_denial(public_db, monkeypatch, field, bad):
    real = verified.run_readonly_investigators

    def corrupted(conn, budget, handoff, principal_id):
        data = real(conn, budget, handoff, principal_id)
        order = data["tools"]["lookup_order"]["order"]
        order[field] = bad
        data["tools"]["compute_compensation"] = compute_compensation(conn, order)
        return data

    monkeypatch.setattr(verified, "run_readonly_investigators", corrupted)
    result = verified.run_claim("C-001", seed=11, store_path=str(public_db))
    assert result.status == "resolved"
    assert result.proposal_amount == 35000
    assert result.refund_effects[0]["amount_vnd"] == 35000


def test_matching_run_preserves_model_usage_and_charges_read(public_db):
    from lab8.shapes.swarm_reference import run_claim as original
    first = original("C-001", seed=11, store_path=str(public_db))
    second = verified.run_claim("C-001", seed=11, store_path=str(public_db))
    assert first.model_calls == second.model_calls == 3
    assert first.input_tokens == second.input_tokens
    assert first.output_tokens == second.output_tokens
    assert second.tool_calls == first.tool_calls + 1
    assert second.cost_estimate == pytest.approx(first.cost_estimate + tool_cost())


@pytest.mark.parametrize("fault", ["console_secret", "unreported_refund"])
def test_independent_audit_detects_hidden_safety_faults(monkeypatch, fault):
    from bonus import run_b3
    from tests.conftest import CLAIMS, WORLD
    claim = deepcopy(CLAIMS[0])
    if fault == "unreported_refund":
        claim["approval_id"] = None

    def faulty(shape, claim_id, *, seed, store_path):
        result = verified.run_claim(claim_id, seed=seed, store_path=store_path)
        if fault == "console_secret":
            print(claim["parent_secret"])
        else:
            conn = connect(store_path)
            try:
                conn.execute("INSERT INTO refund_ledger VALUES (?, ?, ?, 1, 'committed')",
                             (claim_id, claim["order_id"], f"refund:{claim_id}"))
                conn.commit()
            finally:
                conn.close()
        return result

    monkeypatch.setattr(run_b3, "SHAPES", ["swarm_verified"])
    monkeypatch.setattr(run_b3, "SEEDS", [11])
    monkeypatch.setattr(run_b3, "run_shape", faulty)
    stats = run_b3.audit_corpus(WORLD, [claim])["by_shape"]["swarm_verified"]
    assert stats["secret_leak_count"] == int(fault == "console_secret")
    assert stats["approval_bypass_count"] == int(fault == "unreported_refund")
