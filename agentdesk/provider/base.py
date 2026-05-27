"""Provider interface.

A provider, given the current request and the tool results gathered so far,
returns the next step: either a tool to call, or a final proposal with a
signal score in [0, 1] expressing how confident the provider is in that
proposal. The agent combines this signal with tool-result completeness to
produce a calibrated confidence.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass
class ProviderStep:
    """One decision from the provider."""

    kind: str  # "tool" or "final"
    tool_name: str | None = None
    tool_arguments: dict[str, Any] | None = None
    proposal: str | None = None
    signal: float = 0.0

    def __post_init__(self) -> None:
        if self.kind not in ("tool", "final"):
            raise ValueError(f"unknown step kind {self.kind}")
        if not 0.0 <= self.signal <= 1.0:
            raise ValueError("signal must be in [0, 1]")


class Provider(Protocol):
    def next_step(
        self, request: dict[str, Any], history: list[dict[str, Any]]
    ) -> ProviderStep: ...
