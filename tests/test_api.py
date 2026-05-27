import json

from agentdesk.api import Handler, build_service_with_samples


class FakeRequest:
    """Minimal stand-in so we can exercise the handler without sockets."""

    def __init__(self, method, path, body=None):
        self.method = method
        self.path = path
        self.body = json.dumps(body).encode() if body is not None else b""


def call(method, path, body=None):
    handler = Handler.__new__(Handler)
    handler.service = build_service_with_samples()
    handler.path = path
    handler.headers = {"Content-Length": str(len(json.dumps(body))) if body else "0"}

    captured = {}

    def fake_send(status, payload):
        captured["status"] = status
        captured["payload"] = payload

    handler._send = fake_send  # type: ignore[method-assign]
    if body is not None:
        import io

        handler.rfile = io.BytesIO(json.dumps(body).encode())
    getattr(handler, f"do_{method}")()
    return captured


def test_queue_lists_samples():
    out = call("GET", "/api/queue")
    assert out["status"] == 200
    assert len(out["payload"]["requests"]) >= 1


def test_escalations_endpoint():
    out = call("GET", "/api/escalations")
    assert out["status"] == 200
    assert all(
        e["resolution"]["status"] == "escalated" for e in out["payload"]["escalations"]
    )


def test_submit_runs_request():
    body = {"id": "X9", "intent": "account_status", "account_id": "A100"}
    out = call("POST", "/api/submit", body)
    assert out["status"] == 200
    assert out["payload"]["request_id"] == "X9"


def test_unknown_path_is_404():
    out = call("GET", "/api/nope")
    assert out["status"] == 404
