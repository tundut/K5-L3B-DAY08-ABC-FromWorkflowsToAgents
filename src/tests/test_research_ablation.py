"""Check the intervention, business outcomes and safety before measuring R1."""

import pytest

from bonus import investigator_ablation as experiment
from lab8.db import connect, init_store
from lab8.durability import InjectedCrash
from lab8.metrics import trial_pass
from lab8.tools import tool_cost
from tests.conftest import BY_ID, CLAIMS, WORLD


@pytest.fixture(autouse=True)
def isolated_artifacts(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)


@pytest.mark.parametrize("claim_id", list(BY_ID))
def test_partition_preserves_outcome_and_charges_extra_read(tmp_path, claim_id, monkeypatch):
    calls = []
    real = experiment.run_readonly_investigators

    def record(conn, budget, handoff, principal_id):
        calls.append(handoff["allowed_tools"])
        return real(conn, budget, handoff, principal_id)

    monkeypatch.setattr(experiment, "run_readonly_investigators", record)
    results = []
    for entry in (experiment.run_one, experiment.run_two):
        store = tmp_path / f"{entry.__name__}.sqlite"
        init_store(store, WORLD, CLAIMS).close()
        result = entry(claim_id, seed=55, store_path=str(store))
        conn = connect(store)
        try:
            assert trial_pass(result.as_dict(), BY_ID[claim_id]["expected"], conn) == (True, "ok")
        finally:
            conn.close()
        results.append(result)
    first, second = results
    assert first.model_calls == second.model_calls == 0
    assert (first.status, first.proposal_amount, first.refund_effects) == (second.status, second.proposal_amount, second.refund_effects)
    if claim_id == "C-004":
        assert calls == []
        assert first.cost_estimate == second.cost_estimate
    else:
        assert calls == [["lookup_order", "lookup_policy"], ["lookup_order"], ["lookup_policy"]]
        assert second.tool_calls == first.tool_calls + 1
        assert second.cost_estimate == pytest.approx(first.cost_estimate + tool_cost())


@pytest.mark.parametrize("entry", [experiment.run_one, experiment.run_two])
@pytest.mark.parametrize("point", ["before_effect", "after_effect_before_checkpoint", "after_checkpoint"])
def test_research_variant_crash_resume_is_idempotent(public_db, entry, point):
    with pytest.raises(InjectedCrash):
        entry("C-014", seed=11, store_path=str(public_db), crash_at=point)
    entry("C-014", seed=11, store_path=str(public_db))
    replay = entry("C-014", seed=11, store_path=str(public_db))
    conn = connect(public_db)
    try:
        assert trial_pass(replay.as_dict(), BY_ID["C-014"]["expected"], conn) == (True, "ok")
    finally:
        conn.close()


@pytest.mark.parametrize("entry", [experiment.run_one, experiment.run_two])
@pytest.mark.parametrize("approval_id", [None, "A-008"])
def test_research_variant_cannot_bypass_missing_or_borrowed_approval(public_db, entry, approval_id):
    conn = connect(public_db)
    try:
        conn.execute("UPDATE claims SET approval_id = ? WHERE claim_id = 'C-001'", (approval_id,))
        conn.commit()
        result = entry("C-001", seed=11, store_path=str(public_db))
        assert result.status == "denied"
        assert result.proposal_amount == 35000
        assert result.refund_effects == []
        assert conn.execute("SELECT COUNT(*) FROM refund_ledger WHERE claim_id = 'C-001'").fetchone()[0] == 0
        assert conn.execute("SELECT COUNT(*) FROM audit_events WHERE claim_id = 'C-001' AND event_type = 'policy_denied'").fetchone()[0] == 1
    finally:
        conn.close()
