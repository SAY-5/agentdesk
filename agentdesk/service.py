"""Service layer that the API and the console use.

Holds a single backend, the agent, and the audit trail of transcripts. It runs
inbound requests, exposes the queue and escalations, and lets a human approve
or override an escalated request (recording the decision in the audit trail).
"""

from __future__ import annotations

from typing import Any

from agentdesk.audit import AuditTrail
from agentdesk.backend import Backend
from agentdesk.core import Agent
from agentdesk.core.confidence import ConfidenceModel
from agentdesk.provider import FakeProvider
from agentdesk.tools import build_registry


class Service:
    def __init__(self, threshold: float | None = None) -> None:
        self._backend = Backend()
        self._registry = build_registry(self._backend)
        confidence = ConfidenceModel(threshold) if threshold is not None else ConfidenceModel()
        self._agent = Agent(self._registry, FakeProvider(), confidence)
        self._audit = AuditTrail()

    def submit(self, request: dict[str, Any]) -> dict[str, Any]:
        transcript = self._agent.handle(request)
        self._audit.record(transcript)
        return transcript.to_dict()

    def queue(self) -> list[dict[str, Any]]:
        return [t.to_dict() for t in self._audit.all()]

    def escalations(self) -> list[dict[str, Any]]:
        return [
            t.to_dict()
            for t in self._audit.all()
            if t.resolution and t.resolution.status == "escalated"
        ]

    def transcript(self, request_id: str) -> dict[str, Any] | None:
        found = self._audit.get(request_id)
        return found.to_dict() if found else None

    def resolve_escalation(
        self, request_id: str, decision: str, note: str = ""
    ) -> dict[str, Any]:
        return self._audit.apply_human_decision(request_id, decision, note)
