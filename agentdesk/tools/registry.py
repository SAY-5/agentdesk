"""MCP-style tool interface.

Each tool has a name, a JSON-schema-like parameter spec, and a handler that
runs against the backend. The registry validates arguments against the schema
before dispatch and refuses any tool name outside the allowlist.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from agentdesk.backend import Backend, BackendError


class ToolError(Exception):
    """Raised when a tool call is invalid or its handler fails."""


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    parameters: dict[str, str]
    handler: Callable[[Backend, dict[str, Any]], dict]

    def validate(self, arguments: dict[str, Any]) -> None:
        for key, kind in self.parameters.items():
            if key not in arguments:
                raise ToolError(f"{self.name}: missing argument {key}")
            value = arguments[key]
            if kind == "string" and not isinstance(value, str):
                raise ToolError(f"{self.name}: {key} must be a string")
            if kind == "number" and not isinstance(value, (int, float)):
                raise ToolError(f"{self.name}: {key} must be a number")
        extra = set(arguments) - set(self.parameters)
        if extra:
            raise ToolError(f"{self.name}: unexpected arguments {sorted(extra)}")


# The tool allowlist. The agent may only call names present here.
TOOLS: tuple[str, ...] = (
    "lookup_order",
    "check_refund_eligibility",
    "issue_refund",
    "update_address",
    "get_account",
)


class ToolRegistry:
    """Holds tool specs and dispatches validated calls to the backend."""

    def __init__(self, backend: Backend, specs: dict[str, ToolSpec]) -> None:
        self._backend = backend
        self._specs = specs

    def names(self) -> tuple[str, ...]:
        return tuple(self._specs)

    def spec(self, name: str) -> ToolSpec:
        if name not in self._specs:
            raise ToolError(f"tool not in allowlist: {name}")
        return self._specs[name]

    def call(self, name: str, arguments: dict[str, Any]) -> dict:
        if name not in self._specs:
            raise ToolError(f"tool not in allowlist: {name}")
        spec = self._specs[name]
        spec.validate(arguments)
        try:
            return spec.handler(self._backend, arguments)
        except BackendError as exc:
            raise ToolError(str(exc)) from exc


def build_registry(backend: Backend) -> ToolRegistry:
    specs = {
        "lookup_order": ToolSpec(
            name="lookup_order",
            description="Fetch an order by id.",
            parameters={"order_id": "string"},
            handler=lambda b, a: b.lookup_order(a["order_id"]),
        ),
        "check_refund_eligibility": ToolSpec(
            name="check_refund_eligibility",
            description="Check whether an order can be refunded.",
            parameters={"order_id": "string"},
            handler=lambda b, a: b.check_refund_eligibility(a["order_id"]),
        ),
        "issue_refund": ToolSpec(
            name="issue_refund",
            description="Issue a refund for an eligible order.",
            parameters={"order_id": "string"},
            handler=lambda b, a: b.issue_refund(a["order_id"]),
        ),
        "update_address": ToolSpec(
            name="update_address",
            description="Update the mailing address on an account.",
            parameters={"account_id": "string", "address": "string"},
            handler=lambda b, a: b.update_address(a["account_id"], a["address"]),
        ),
        "get_account": ToolSpec(
            name="get_account",
            description="Fetch an account record.",
            parameters={"account_id": "string"},
            handler=lambda b, a: b.get_account(a["account_id"]),
        ),
    }
    assert set(specs) == set(TOOLS), "registry must match the allowlist"
    return ToolRegistry(backend, specs)
