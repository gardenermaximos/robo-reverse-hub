"""dispatcher.py — Job queue for the Add-in HTTP server.

Must NOT import adsk at module level so pytest can run outside Fusion.
run_job() does a lazy import of executor (which imports adsk).
"""

from __future__ import annotations

import threading
import time
import uuid

_lock = threading.Lock()
_jobs: dict[str, dict] = {}


def enqueue(plan: dict) -> str:
    job_id = "job_" + uuid.uuid4().hex[:8]
    with _lock:
        _jobs[job_id] = {
            "job_id": job_id,
            "status": "queued",
            "plan": plan,
            "results": [],
            "started_at": None,
            "finished_at": None,
        }
    return job_id


def run_job(job_id: str) -> None:
    """Execute a job. Must be called from the Fusion main thread."""
    from . import executor  # lazy import — keeps this module testable without adsk

    with _lock:
        job = _jobs.get(job_id)
        if job is None:
            return
        job["status"] = "running"
        job["started_at"] = time.time()

    try:
        results = executor.execute_plan(job["plan"])
        failed = any(r["status"] == "error" for r in results)
        with _lock:
            job["results"] = results
            job["status"] = "failed" if failed else "done"
    except Exception as e:
        with _lock:
            job["status"] = "failed"
            job["results"] = [{"command_id": None, "status": "error", "error": str(e)}]
    finally:
        with _lock:
            job["finished_at"] = time.time()


def get(job_id: str) -> dict | None:
    with _lock:
        job = _jobs.get(job_id)
        if job is None:
            return None
        # Return a copy without the plan payload
        return {k: v for k, v in job.items() if k != "plan"}
