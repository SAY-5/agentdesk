"""The agent loop.

Given an inbound request, the agent asks the provider for the next step. If
the step is a tool call, it validates and dispatches it through the registry,
records the result, and loops. If the step is final, it scores confidence from
the provider signal and the tool-call success rate, then either resolves the
request or escalates it to a human.
"""

from __future__ import annotations

from typing import Any

from agentdesk.core.confidence import ConfidenceModel
from agentdesk.core.result import Resolution, ToolCall, Transcript
from agentdesk.provider.base import Provider
from agentdesk.tools import ToolError, ToolRegistry

MAX_STEPS = 8


class Agent:
    def __init__(
        self,
        registry: ToolRegistry,
        provider: Provider,
        confidence: ConfidenceModel | None = None,
    ) -> None:
        self._registry = registry
        self._provider = provider
        self._confidence = confidence or ConfidenceModel()

    def handle(self, request: dict[str, Any]) -> Transcript:
        request_id = str(request.get("id", "req"))
        transcript = Transcript(request_id=request_id, request=dict(request))
        history: list[dict[str, Any]] = []

        for _ in range(MAX_STEPS):
            step = self._provider.next_step(request, history)
            transcript.provider_signals.append(step.signal)

            if step.kind == "final":
                self._finalize(transcript, step.proposal or "", step.signal)
                return transcript

            call = self._run_tool(step.tool_name or "", step.tool_arguments or {})
            transcript.tool_calls.append(call)
            history.append(
                {"tool": call.name, "ok": call.ok, "result": call.result, "error": call.error}
            )

        # Ran out of steps without a final proposal: escalate.
        self._escalate(transcript, "step budget exhausted", 0.0)
        return transcript

    def _run_tool(self, name: str, arguments: dict[str, Any]) -> ToolCall:
        try:
            result = self._registry.call(name, arguments)
            return ToolCall(name=name, arguments=arguments, ok=True, result=result)
        except ToolError as exc:
            return ToolCall(name=name, arguments=arguments, ok=False, error=str(exc))

    def _completeness(self, transcript: Transcript) -> float:
        calls = transcript.tool_calls
        if not calls:
            return 1.0
        ok = sum(1 for c in calls if c.ok)
        return ok / len(calls)

    def _finalize(self, transcript: Transcript, proposal: str, signal: float) -> None:
        completeness = self._completeness(transcript)
        confidence, escalate = self._confidence.decide(signal, completeness)
        if escalate:
            self._escalate(transcript, "confidence below threshold", confidence)
        else:
            transcript.resolution = Resolution(
                request_id=transcript.request_id,
                status="resolved",
                proposal=proposal,
                confidence=confidence,
                reason="confidence at or above threshold",
            )

    def _escalate(self, transcript: Transcript, reason: str, confidence: float) -> None:
        transcript.resolution = Resolution(
            request_id=transcript.request_id,
            status="escalated",
            proposal="",
            confidence=confidence,
            reason=reason,
        )
