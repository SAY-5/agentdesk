"""Confidence model and escalation threshold.

Confidence combines two observable quantities gathered while handling a
request:

  signal       the provider's own confidence in its final proposal, in [0, 1]
  completeness the fraction of the agent's tool calls that succeeded, in [0, 1]

Both must be high for the agent to act on its own. We take their product so
that a weak provider signal OR a failed tool call pulls confidence down. A
request whose confidence is at or above the threshold is auto-resolved; below
it the request escalates to a human. The threshold is tunable so operators can
trade automation rate against the risk of acting when unsure.
"""

from __future__ import annotations

from dataclasses import dataclass

DEFAULT_THRESHOLD = 0.7


def score_confidence(signal: float, completeness: float) -> float:
    """Combine provider signal and tool-result completeness into [0, 1]."""
    if not 0.0 <= signal <= 1.0:
        raise ValueError("signal must be in [0, 1]")
    if not 0.0 <= completeness <= 1.0:
        raise ValueError("completeness must be in [0, 1]")
    return round(signal * completeness, 4)


@dataclass
class ConfidenceModel:
    """Decides whether a scored request is auto-resolved or escalated."""

    threshold: float = DEFAULT_THRESHOLD

    def __post_init__(self) -> None:
        if not 0.0 <= self.threshold <= 1.0:
            raise ValueError("threshold must be in [0, 1]")

    def should_escalate(self, confidence: float) -> bool:
        return confidence < self.threshold

    def decide(self, signal: float, completeness: float) -> tuple[float, bool]:
        confidence = score_confidence(signal, completeness)
        return confidence, self.should_escalate(confidence)
