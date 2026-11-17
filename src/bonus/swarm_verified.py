"""B3 variant derived from lab8/shapes/swarm_reference.py (starter repo).

The original peer/parse/draft calls and model override remain intact.
A scoped structured-order verifier runs after drafting and before any return
or host write. The original reference file is never modified.

Shape D — reference swarm. Provided so the lab can compare, not so it wins.

Peers talk (extra model calls). On seed % 5 == 0 the swarm trusts a delay
written in the ticket when that number disagrees with the order row. That is
the variance you should measure. The host still blocks writes that fail
approval, ownership, or idempotency.
"""

from __future__ import annotations

import sqlite3

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.handoff import make_handoff
from lab8.mock_llm import complete, parse_delay_days
from lab8.runtime import run_readonly_investigators
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish, safe_dump
from lab8.tools import compute_compensation, lookup_order, tool_cost


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    conn = connect(store_path)
    try:
        return _run(conn, claim_id, seed=seed, crash_at=crash_at)
    finally:
        conn.close()


def _run(conn: sqlite3.Connection, claim_id: str, *, seed: int, crash_at: str | None) -> RunResult:
    budget = Budget()
    run_id = make_run_id("swarm_verified", claim_id, seed)
    trace = _Trace(run_id)
    budget.add_tool(tool_cost())
    claim_row = conn.execute(
        "SELECT claim_id, principal_id, order_id, ticket FROM claims WHERE claim_id = ?",
        (claim_id,),
    ).fetchone()
    if claim_row is None:
        trace.add("error", {"reason": "unknown_claim"})
        return finish(
            conn,
            shape="swarm_verified",
            claim_id=claim_id,
            seed=seed,
            status="failed",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason="unknown_claim",
        )

    ticket = claim_row["ticket"]
    complete(budget, seed=seed, purpose="peer", prompt=ticket)
    parsed_delay = parse_delay_days(ticket)
    complete(budget, seed=seed, purpose="parse", prompt=ticket)

    if not claim_row["order_id"]:
        complete(budget, seed=seed, purpose="draft", prompt="needs_info")
        trace.add("decision", {"status": "needs_info"})
        return finish(
            conn,
            shape="swarm_verified",
            claim_id=claim_id,
            seed=seed,
            status="needs_info",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason="missing_order_id",
        )

    handoff = make_handoff(
        request_id=f"REQ-{claim_id}",
        claim_id=claim_id,
        task="check_applicable_policy",
        facts={},
        allowed_tools=["lookup_order", "lookup_policy", "compute_compensation"],
    )
    trace.add("handoff", safe_dump(handoff))
    investigated = run_readonly_investigators(
        conn, budget, handoff, principal_id=claim_row["principal_id"]
    )
    order_view = investigated["tools"].get("lookup_order", {})
    trace.add("investigator", {"lookup_order": order_view, "policy_count": len((investigated["tools"].get("lookup_policy") or {}).get("policies") or [])})
    if not order_view.get("visible"):
        complete(budget, seed=seed, purpose="draft", prompt="escalated")
        return finish(
            conn,
            shape="swarm_verified",
            claim_id=claim_id,
            seed=seed,
            status="escalated",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason=order_view.get("reason"),
        )

    order = dict(order_view["order"])
    # REFERENCE_WEAKNESS: one seed in five trusts the ticket delay over the DB.
    if parsed_delay is not None and parsed_delay != int(order["delay_days"]) and seed % 5 == 0:
        order["delay_days"] = parsed_delay
        trace.add("model_override", {"delay_days": parsed_delay})

    quote_payload = investigated["tools"]["compute_compensation"]
    # Recompute if the weakness rewrote delay. Otherwise keep the investigator quote.
    if order["delay_days"] != order_view["order"]["delay_days"]:
        from lab8.tools import compute_compensation

        budget.add_tool(tool_cost())
        quote_payload = compute_compensation(conn, order)
    proposal = int(quote_payload["amount_vnd"])
    trace.add("quote", quote_payload)
    complete(budget, seed=seed, purpose="draft", prompt=f"proposal={proposal}")

    # Independent read: do not trust the investigator's mutable order view.
    checked = verify_quote(conn, budget, order, quote_payload,
                           order_id=claim_row["order_id"], principal_id=claim_row["principal_id"])
    trace.add("verifier_checked", {"visible": checked["visible"]})
    if not checked["visible"]:
        return finish(conn, shape="swarm_verified", claim_id=claim_id, seed=seed,
                      status="escalated", proposal_amount=0, budget=budget, trace=trace,
                      error_reason=checked["reason"])
    if checked["changed_fields"]:
        trace.add("verifier_override", {"changed_fields": checked["changed_fields"],
                                       "previous_amount_vnd": proposal,
                                       "corrected_amount_vnd": checked["quote"]["amount_vnd"]})
    quote_payload = checked["quote"]
    proposal = int(quote_payload["amount_vnd"])
    trace.add("verified_quote", quote_payload)

    if proposal <= 0:
        return finish(
            conn,
            shape="swarm_verified",
            claim_id=claim_id,
            seed=seed,
            status="denied",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason=quote_payload.get("reason"),
        )

    try:
        outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    except InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise

    if not outcome["ok"]:
        status = "failed" if outcome["conflict"] else "denied"
        return finish(
            conn,
            shape="swarm_verified",
            claim_id=claim_id,
            seed=seed,
            status=status,
            proposal_amount=proposal,
            budget=budget,
            trace=trace,
            error_reason=outcome["reason"],
        )
    return finish(
        conn,
        shape="swarm_verified",
        claim_id=claim_id,
        seed=seed,
        status="resolved",
        proposal_amount=proposal,
        budget=budget,
        trace=trace,
        error_reason=None,
    )


class _Trace:
    """Local alias so a crash can still flush. Wraps lab8.trace.Trace."""

    def __init__(self, run_id: str) -> None:
        from lab8.trace import Trace

        self._inner = Trace(run_id)

    def add(self, kind: str, payload: dict) -> None:
        self._inner.add(kind, payload)

    def write(self) -> str:
        return self._inner.write()

    @property
    def run_id(self) -> str:
        return self._inner.run_id


QUOTE_FIELDS = ("delay_days", "status", "damage_verified", "shipping_fee_vnd", "paid_vnd")


def verify_quote(conn, budget: Budget, candidate_order: dict, candidate_quote: dict,
                 *, order_id: str, principal_id: str) -> dict:
    """One verification, at most one correction. Canonical data stays host-scoped.

    Every run pays for the independent read. A mismatch pays for one additional
    quote tool call. No LLM call, mutation of the source order or host bypass.
    """
    budget.add_tool(tool_cost())
    canonical = lookup_order(conn, order_id, principal_id)
    if not canonical["visible"]:
        return {"visible": False, "reason": canonical["reason"]}
    order = canonical["order"]
    changed = [key for key in QUOTE_FIELDS if candidate_order.get(key) != order.get(key)]
    quote = candidate_quote
    if changed:
        budget.add_tool(tool_cost())
        quote = compute_compensation(conn, order)
    return {"visible": True, "changed_fields": changed, "quote": quote}
