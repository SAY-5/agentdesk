"""Contract tests for the tool interface.

These assert the invariants the agent relies on: every call is schema-checked,
no tool outside the allowlist is reachable, and a backend failure surfaces as a
ToolError rather than crashing the loop.
"""

import pytest

from agentdesk.backend import Backend
from agentdesk.tools import TOOLS, ToolError, build_registry

EVERY_TOOL = list(TOOLS)


@pytest.fixture
def registry():
    return build_registry(Backend())


def test_registry_exposes_exactly_the_allowlist(registry):
    assert set(registry.names()) == set(TOOLS)


@pytest.mark.parametrize("name", EVERY_TOOL)
def test_every_tool_has_a_spec_with_parameters(registry, name):
    spec = registry.spec(name)
    assert spec.name == name
    assert isinstance(spec.parameters, dict)


@pytest.mark.parametrize("name", EVERY_TOOL)
def test_every_tool_rejects_missing_arguments(registry, name):
    with pytest.raises(ToolError):
        registry.call(name, {})


@pytest.mark.parametrize("name", EVERY_TOOL)
def test_every_tool_rejects_unexpected_arguments(registry, name):
    spec = registry.spec(name)
    args = {key: "x" for key in spec.parameters}
    args["surprise"] = 1
    with pytest.raises(ToolError):
        registry.call(name, args)


@pytest.mark.parametrize("name", ["", "drop_table", "lookup_orderr", "GET_ACCOUNT"])
def test_names_outside_allowlist_are_refused(registry, name):
    with pytest.raises(ToolError):
        registry.call(name, {})


@pytest.mark.parametrize("order_id", ["", "ghost", "O9999", "123"])
def test_backend_failure_becomes_tool_error(registry, order_id):
    with pytest.raises(ToolError):
        registry.call("lookup_order", {"order_id": order_id})


def test_string_argument_must_be_a_string(registry):
    with pytest.raises(ToolError):
        registry.call("lookup_order", {"order_id": 123})
