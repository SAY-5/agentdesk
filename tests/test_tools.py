import pytest

from agentdesk.backend import Backend
from agentdesk.tools import TOOLS, ToolError, build_registry


def test_registry_matches_allowlist():
    registry = build_registry(Backend())
    assert set(registry.names()) == set(TOOLS)


def test_call_outside_allowlist_is_refused():
    registry = build_registry(Backend())
    with pytest.raises(ToolError):
        registry.call("delete_everything", {})


def test_missing_argument_is_rejected():
    registry = build_registry(Backend())
    with pytest.raises(ToolError):
        registry.call("lookup_order", {})


def test_unexpected_argument_is_rejected():
    registry = build_registry(Backend())
    with pytest.raises(ToolError):
        registry.call("lookup_order", {"order_id": "O1001", "extra": 1})


def test_backend_error_becomes_tool_error():
    registry = build_registry(Backend())
    with pytest.raises(ToolError):
        registry.call("lookup_order", {"order_id": "missing"})


def test_valid_call_returns_result():
    registry = build_registry(Backend())
    result = registry.call("get_account", {"account_id": "A100"})
    assert result["name"] == "Dana Reyes"
