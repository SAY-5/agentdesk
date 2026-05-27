"""Audit trail and human-in-loop resolution.

Every handled request is stored as a transcript. A human can replay an
escalation (re-read its full trace) and approve or override it; that decision
is recorded back onto the transcript so the record is complete.
"""

from __future__ import annotations

from typing import Any

from agentdesk.core.result import Resolution, Transcript

VALID_DECISIONS = ("approve", "override")


class AuditError(Exception):
    """Raised on an invalid human-in-loop action."""


class AuditTrail:
    def __init__(self) -> None:
        self._by_id: dict[str, Transcript] = {}
        self._order: list[str] = []

    def record(self, transcript: Transcript) -> None:
        if transcript.request_id not in self._by_id:
            self._order.append(transcript.request_id)
        self._by_id[transcript.request_id] = transcript

    def all(self) -> list[Transcript]:
        return [self._by_id[rid] for rid in self._order]

    def get(self, request_id: str) -> Transcript | None:
        return self._by_id.get(request_id)

    def replay(self, request_id: str) -> dict[str, Any]:
        """Return the full trace of a request for human review."""
        transcript = self._by_id.get(request_id)
        if transcript is None:
            raise AuditError(f"unknown request {request_id}")
        return transcript.to_dict()

    def apply_human_decision(
        self, request_id: str, decision: str, note: str = ""
    ) -> dict[str, Any]:
        transcript = self._by_id.get(request_id)
        if transcript is None:
            raise AuditError(f"unknown request {request_id}")
        if transcript.resolution is None or transcript.resolution.status != "escalated":
            raise AuditError("only escalated requests accept a human decision")
        if decision not in VALID_DECISIONS:
            raise AuditError(f"unknown decision {decision}")

        transcript.human_decision = {"decision": decision, "note": note}
        if decision == "approve":
            proposal = "approved by human"
            reason = "human approved the proposed action"
        else:
            proposal = note or "handled manually by human"
            reason = "human overrode the proposed action"
        transcript.resolution = Resolution(
            request_id=request_id,
            status="resolved",
            proposal=proposal,
            confidence=transcript.resolution.confidence,
            reason=reason,
        )
        return transcript.to_dict()
