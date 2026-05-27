"""A small JSON HTTP API over the service, for the oversight console.

Stdlib only so it stays dependency-free and starts fast in CI and compose.

  GET  /api/queue                 list all handled requests
  GET  /api/escalations           list requests awaiting a human
  GET  /api/transcript/{id}       full trace for one request
  POST /api/submit                {request...} run a request through the agent
  POST /api/escalations/{id}      {decision, note} approve or override
"""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from agentdesk.audit import AuditError
from agentdesk.sample_requests import SAMPLE_REQUESTS
from agentdesk.service import Service


def build_service_with_samples() -> Service:
    service = Service()
    for request in SAMPLE_REQUESTS:
        service.submit(request)
    return service


class Handler(BaseHTTPRequestHandler):
    service: Service

    def log_message(self, *args: Any) -> None:  # silence default logging
        return

    def _send(self, status: int, payload: Any) -> None:
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length).decode() or "{}")

    def do_OPTIONS(self) -> None:
        self._send(204, {})

    def do_GET(self) -> None:
        path = self.path.rstrip("/")
        if path == "/api/queue":
            self._send(200, {"requests": self.service.queue()})
        elif path == "/api/escalations":
            self._send(200, {"escalations": self.service.escalations()})
        elif path.startswith("/api/transcript/"):
            request_id = path.rsplit("/", 1)[-1]
            found = self.service.transcript(request_id)
            if found is None:
                self._send(404, {"error": "not found"})
            else:
                self._send(200, found)
        elif path in ("/api/health", "/health"):
            self._send(200, {"status": "ok"})
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self) -> None:
        path = self.path.rstrip("/")
        try:
            body = self._read_json()
        except json.JSONDecodeError:
            self._send(400, {"error": "invalid json"})
            return

        if path == "/api/submit":
            self._send(200, self.service.submit(body))
        elif path.startswith("/api/escalations/"):
            request_id = path.rsplit("/", 1)[-1]
            try:
                result = self.service.resolve_escalation(
                    request_id, body.get("decision", ""), body.get("note", "")
                )
                self._send(200, result)
            except AuditError as exc:
                self._send(400, {"error": str(exc)})
        else:
            self._send(404, {"error": "not found"})


def serve(host: str = "0.0.0.0", port: int | None = None) -> None:
    port = port or int(os.environ.get("PORT", "8000"))
    Handler.service = build_service_with_samples()
    server = ThreadingHTTPServer((host, port), Handler)
    server.serve_forever()


if __name__ == "__main__":
    serve()
