"""Deterministic fake provider used in CI.

It maps a request intent to a fixed plan of tool calls and a final proposal.
No network, no randomness: the same request always yields the same steps. The
signal it reports depends on whether the request carries the fields its plan
needs, so under-specified requests get a low signal and escalate.
"""

from __future__ import annotations

from typing import Any

from agentdesk.provider.base import ProviderStep


class FakeProvider:
    """A rule-based provider keyed on the request intent."""

    def next_step(
        self, request: dict[str, Any], history: list[dict[str, Any]]
    ) -> ProviderStep:
        intent = request.get("intent", "")
        called = {h["tool"] for h in history if h.get("tool")}
        handler = getattr(self, f"_plan_{intent}", self._plan_unknown)
        return handler(request, called)

    def _plan_refund(self, request: dict[str, Any], called: set[str]) -> ProviderStep:
        order_id = request.get("order_id")
        if not order_id:
            return ProviderStep(kind="final", proposal="cannot locate order", signal=0.1)
        if "lookup_order" not in called:
            return ProviderStep(
                kind="tool", tool_name="lookup_order",
                tool_arguments={"order_id": order_id}, signal=0.6,
            )
        if "check_refund_eligibility" not in called:
            return ProviderStep(
                kind="tool", tool_name="check_refund_eligibility",
                tool_arguments={"order_id": order_id}, signal=0.7,
            )
        if "issue_refund" not in called:
            return ProviderStep(
                kind="tool", tool_name="issue_refund",
                tool_arguments={"order_id": order_id}, signal=0.85,
            )
        return ProviderStep(
            kind="final", proposal=f"refund issued for {order_id}", signal=0.92
        )

    def _plan_address(self, request: dict[str, Any], called: set[str]) -> ProviderStep:
        account_id = request.get("account_id")
        address = request.get("address")
        if not account_id or not address:
            return ProviderStep(
                kind="final", proposal="missing account or address", signal=0.15
            )
        if "update_address" not in called:
            return ProviderStep(
                kind="tool", tool_name="update_address",
                tool_arguments={"account_id": account_id, "address": address},
                signal=0.8,
            )
        return ProviderStep(
            kind="final", proposal=f"address updated for {account_id}", signal=0.9
        )

    def _plan_account_status(
        self, request: dict[str, Any], called: set[str]
    ) -> ProviderStep:
        account_id = request.get("account_id")
        if not account_id:
            return ProviderStep(
                kind="final", proposal="missing account id", signal=0.2
            )
        if "get_account" not in called:
            return ProviderStep(
                kind="tool", tool_name="get_account",
                tool_arguments={"account_id": account_id}, signal=0.75,
            )
        return ProviderStep(
            kind="final", proposal=f"account summary for {account_id}", signal=0.88
        )

    def _plan_unknown(self, request: dict[str, Any], called: set[str]) -> ProviderStep:
        # No matching plan: low signal so the request escalates.
        return ProviderStep(
            kind="final", proposal="no automated plan for this request", signal=0.2
        )
