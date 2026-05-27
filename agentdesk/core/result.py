"""Result and transcript types produced by the agent."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ToolCall:
    name: str
    arguments: dict[str, Any]
    ok: bool
    result: dict[str, Any] | None = None
    error: str | None = None


@dataclass
class Resolution:
    request_id: str
    status: str  # "resolved" or "escalated"
    proposal: str
    confidence: float
    reason: str


@dataclass
class Transcript:
    """Full record of one request being handled, used by the audit layer."""

    request_id: str
    request: dict[str, Any]
    tool_calls: list[ToolCall] = field(default_factory=list)
    provider_signals: list[float] = field(default_factory=list)
    resolution: Resolution | None = None
    human_decision: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "request": self.request,
            "tool_calls": [asdict(c) for c in self.tool_calls],
            "provider_signals": list(self.provider_signals),
            "resolution": asdict(self.resolution) if self.resolution else None,
            "human_decision": self.human_decision,
        }
