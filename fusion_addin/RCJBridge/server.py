"""server.py — ThreadingHTTPServer for the RCJBridge Add-in.

Runs in a daemon thread; communicates with the Fusion main thread via on_enqueue callback.
"""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Callable

from . import dispatcher, validate as _validate

_server: HTTPServer | None = None
_on_enqueue: Callable[[str], None] | None = None


def _load_config() -> dict:
    import os
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    with open(config_path, encoding="utf-8") as f:
        return json.load(f)


_cfg = _load_config()
_TOKEN = _cfg.get("token", "")
_MAX_BODY = _cfg.get("max_body_bytes", 2_000_000)


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):  # noqa: A002
        pass  # suppress default HTTP logs; use Fusion's app.log instead

    def _auth(self) -> bool:
        return self.headers.get("X-RCJ-Token") == _TOKEN

    def _send_json(self, code: int, data: dict) -> None:
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self) -> bytes | None:
        length = int(self.headers.get("Content-Length", 0))
        if length > _MAX_BODY:
            self._send_json(413, {"error": "Request body too large"})
            return None
        return self.rfile.read(length)

    def do_GET(self):
        if not self._auth():
            self._send_json(401, {"error": "Unauthorized"})
            return

        if self.path == "/health":
            self._send_json(200, {"ok": True, "addin_version": "0.1.0"})

        elif self.path.startswith("/jobs/"):
            job_id = self.path[len("/jobs/"):]
            job = dispatcher.get(job_id)
            if job is None:
                self._send_json(404, {"error": f"Job {job_id!r} not found"})
            else:
                self._send_json(200, job)
        else:
            self._send_json(404, {"error": "Not found"})

    def do_POST(self):
        if not self._auth():
            self._send_json(401, {"error": "Unauthorized"})
            return

        body = self._read_body()
        if body is None:
            return

        try:
            plan = json.loads(body)
        except json.JSONDecodeError as e:
            self._send_json(400, {"error": f"Invalid JSON: {e}"})
            return

        if self.path == "/validate":
            errors, warnings = _validate.validate_plan(plan)
            self._send_json(200, {"ok": not errors, "errors": errors, "warnings": warnings})

        elif self.path == "/execute":
            errors, warnings = _validate.validate_plan(plan)
            if errors:
                self._send_json(422, {"ok": False, "errors": errors, "warnings": warnings})
                return
            job_id = dispatcher.enqueue(plan)
            if _on_enqueue:
                _on_enqueue(job_id)
            self._send_json(202, {"job_id": job_id})

        else:
            self._send_json(404, {"error": "Not found"})


def start(on_enqueue: Callable[[str], None]) -> None:
    global _server, _on_enqueue
    _on_enqueue = on_enqueue
    host = _cfg.get("host", "127.0.0.1")
    port = _cfg.get("port", 8765)
    _server = HTTPServer((host, port), _Handler)
    t = threading.Thread(target=_server.serve_forever, daemon=True, name="RCJBridge-HTTP")
    t.start()


def stop() -> None:
    global _server
    if _server:
        _server.shutdown()
        _server.server_close()
        _server = None
