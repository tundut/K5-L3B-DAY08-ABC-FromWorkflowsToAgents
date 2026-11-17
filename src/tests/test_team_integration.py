"""Leader acceptance: an early-return retry must replace a stale trace."""

import os
import time
from pathlib import Path

import pytest

from lab8.db import connect
from lab8.metrics import check_trace
from lab8.shapes import SHAPES


@pytest.mark.parametrize("shape", ["workflow", "single", "orchestrator"])
@pytest.mark.parametrize("claim_id,status", [("C-004", "needs_info"), ("C-005", "escalated"), ("C-UNKNOWN", "failed")])
def test_early_return_retry_replaces_stale_trace(public_db, tmp_path, monkeypatch, shape, claim_id, status):
    monkeypatch.chdir(tmp_path)
    conn = connect(public_db)
    try:
        before = [tuple(row) for row in conn.execute("SELECT * FROM refund_ledger ORDER BY claim_id")]
        first = SHAPES[shape](claim_id, seed=11, store_path=str(public_db))
        path = Path(first.trace_path)
        path.write_text('{"run_id":"STALE","events":[]}', encoding="utf-8")
        os.utime(path, (time.time() - 3600, time.time() - 3600))
        started = time.time()
        retry = SHAPES[shape](claim_id, seed=11, store_path=str(public_db))
        assert check_trace(retry.as_dict(), started_at=started) == (True, "ok")
        assert first.status == retry.status == status
        assert retry.proposal_amount == 0
        assert retry.refund_effects == []
        assert retry.committed_audit_count == 0
        assert [tuple(row) for row in conn.execute("SELECT * FROM refund_ledger ORDER BY claim_id")] == before
    finally:
        conn.close()
