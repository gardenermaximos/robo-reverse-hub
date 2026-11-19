"""send_example_to_fusion.py — Smoke test script: send a CadPlan directly to the Add-in.

Usage (from project root):
    python scripts/send_example_to_fusion.py schemas/examples/smoke_disc_4holes.cadplan.json

Options:
    --token TOKEN     Override the default token (default: troque-este-token)
    --url URL         Add-in base URL (default: http://127.0.0.1:8765)
    --timeout SECS    Polling timeout in seconds (default: 120)
"""

import argparse
import json
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError


def post_json(url: str, data: dict, token: str, timeout: float = 30) -> dict:
    body = json.dumps(data).encode()
    req = Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("X-RCJ-Token", token)
    with urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def get_json(url: str, token: str, timeout: float = 10) -> dict:
    req = Request(url)
    req.add_header("X-RCJ-Token", token)
    with urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def main():
    parser = argparse.ArgumentParser(description="Send a CadPlan to the RCJBridge Add-in")
    parser.add_argument("plan_file", help="Path to the CadPlan JSON file")
    parser.add_argument("--token", default="troque-este-token")
    parser.add_argument("--url", default="http://127.0.0.1:8765")
    parser.add_argument("--timeout", type=float, default=120.0)
    args = parser.parse_args()

    plan_path = Path(args.plan_file)
    if not plan_path.exists():
        print(f"ERROR: file not found: {plan_path}", file=sys.stderr)
        sys.exit(1)

    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    base = args.url.rstrip("/")

    # 1. Health check
    print("Checking Add-in health…")
    try:
        health = get_json(f"{base}/health", args.token)
        print(f"  Add-in OK: {health}")
    except URLError as e:
        print(f"ERROR: Add-in not reachable at {base} — {e}", file=sys.stderr)
        sys.exit(1)

    # 2. Validate
    print("Validating plan…")
    result = post_json(f"{base}/validate", plan, args.token)
    if not result.get("ok"):
        print(f"ERROR: Validation failed: {result['errors']}", file=sys.stderr)
        sys.exit(1)
    if result.get("warnings"):
        for w in result["warnings"]:
            print(f"  WARNING: {w}")

    # 3. Execute
    print("Sending plan for execution…")
    resp = post_json(f"{base}/execute", plan, args.token, timeout=30)
    job_id = resp["job_id"]
    print(f"  job_id: {job_id}")

    # 4. Poll
    deadline = time.time() + args.timeout
    while time.time() < deadline:
        job = get_json(f"{base}/jobs/{job_id}", args.token)
        status = job["status"]
        if status in ("done", "failed"):
            break
        print(f"  status: {status} — polling…")
        time.sleep(0.5)
    else:
        print("ERROR: Timeout waiting for job", file=sys.stderr)
        sys.exit(1)

    # 5. Report
    print(f"\n=== ExecutionReport (job_id={job_id}, status={status}) ===")
    for r in job.get("results", []):
        icon = "✓" if r["status"] == "ok" else "✗"
        line = f"  {icon} [{r['command_id']}] {r['status']}"
        if r.get("info"):
            line += f"  info={r['info']}"
        if r.get("error"):
            line += f"  error={r['error']}"
        print(line)

    if status == "failed":
        sys.exit(1)
    print("\nSmoke test passed.")


if __name__ == "__main__":
    main()
