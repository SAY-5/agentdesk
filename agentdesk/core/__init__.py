"""Agent core: the loop, the confidence model, and the result types."""

from agentdesk.core.agent import Agent
from agentdesk.core.confidence import ConfidenceModel, score_confidence
from agentdesk.core.result import Resolution, ToolCall, Transcript

__all__ = [
    "Agent",
    "ConfidenceModel",
    "score_confidence",
    "Resolution",
    "ToolCall",
    "Transcript",
]
