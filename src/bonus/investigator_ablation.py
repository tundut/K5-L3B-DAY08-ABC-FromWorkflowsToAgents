"""R1: split the same read work across one or two sequential investigators.

Both variants share decisions, quote calculation and host writes. Only the
handoff partition changes; the runtime's extra claim read is charged normally.
No LLM is called in either variant, matching the official orchestrator.
"""

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.handoff import make_handoff
from lab8.runtime import run_readonly_investigators
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish
from lab8.tools import compute_compensation, get_claim_view, tool_cost
from lab8.trace import Trace


def run_one(claim_id: str, *, seed: int, store_path: str, crash_at: str | None = None) -> RunResult:
    return _run(claim_id, seed=seed, store_path=store_path, crash_at=crash_at, workers=1)


def run_two(claim_id: str, *, seed: int, store_path: str, crash_at: str | None = None) -> RunResult:
    return _run(claim_id, seed=seed, store_path=store_path, crash_at=crash_at, workers=2)


def _run(claim_id, *, seed, store_path, crash_at, workers):
    shape = "investigator_one" if workers == 1 else "investigator_two"
    budget = Budget()
    trace = Trace(make_run_id(shape, claim_id, seed))
    conn = connect(store_path)

    def done(status, proposal=0, reason=None):
        trace.add("decision", {"status": status, "reason": reason})
        return finish(conn, shape=shape, claim_id=claim_id, seed=seed,
                      status=status, proposal_amount=proposal, budget=budget,
                      trace=trace, error_reason=reason)

    try:
        budget.add_tool(tool_cost())
        claim = get_claim_view(conn, claim_id)
        trace.add("claim", {"found": claim["found"]})
        if not claim["found"]:
            return done("failed", reason="unknown_claim")
        if not claim.get("order_id"):
            return done("needs_info", reason="missing_order_id")

        partitions = [["lookup_order", "lookup_policy"]] if workers == 1 else [["lookup_order"], ["lookup_policy"]]
        gathered = {}
        for index, tools in enumerate(partitions):
            handoff = make_handoff(request_id=f"REQ-{claim_id}-{index}", claim_id=claim_id,
                                   task="read_order_and_policy", facts={}, allowed_tools=tools)
            trace.add("handoff", handoff)
            investigated = run_readonly_investigators(conn, budget, handoff, principal_id=claim["principal_id"])
            gathered.update(investigated["tools"])
            trace.add("investigator", {"tools": list(investigated["tools"])})

        order_view = gathered["lookup_order"]
        if not order_view["visible"]:
            return done("escalated", reason=order_view["reason"])
        # Same code in both arms; the official adapter selects current policies.
        budget.add_tool(tool_cost())
        quote = compute_compensation(conn, order_view["order"])
        proposal = int(quote["amount_vnd"])
        trace.add("quote", quote)
        if proposal <= 0:
            return done("denied", reason=quote["reason"])
        outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
        if outcome["ok"]:
            return done("resolved", proposal)
        return done("failed" if outcome["conflict"] else "denied", proposal, outcome["reason"])
    except InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise
    finally:
        conn.close()
