"""test_dispatcher.py — Tests for the dispatcher (no adsk required)."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from RCJBridge import dispatcher


def test_enqueue_returns_job_id():
    plan = {"units": "mm", "commands": []}
    job_id = dispatcher.enqueue(plan)
    assert job_id.startswith("job_")


def test_get_queued_job():
    plan = {"units": "mm", "commands": []}
    job_id = dispatcher.enqueue(plan)
    job = dispatcher.get(job_id)
    assert job is not None
    assert job["status"] == "queued"
    assert job["job_id"] == job_id
    # Plan payload should NOT be in the returned dict
    assert "plan" not in job


def test_get_unknown_job():
    result = dispatcher.get("job_does_not_exist")
    assert result is None


def test_enqueue_multiple():
    plan = {"units": "mm", "commands": []}
    ids = {dispatcher.enqueue(plan) for _ in range(5)}
    assert len(ids) == 5  # all unique
