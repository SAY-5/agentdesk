from agentdesk.backend import Backend
from agentdesk.core import Agent
from agentdesk.provider import FakeProvider
from agentdesk.tools import build_registry


def make_agent(threshold=None):
    backend = Backend()
    registry = build_registry(backend)
    from agentdesk.core.confidence import ConfidenceModel

    confidence = ConfidenceModel(threshold) if threshold is not None else None
    return Agent(registry, FakeProvider(), confidence)


def test_refund_request_runs_tools_and_resolves():
    agent = make_agent()
    transcript = agent.handle(
        {"id": "R1", "intent": "refund", "order_id": "O1001"}
    )
    names = [c.name for c in transcript.tool_calls]
    assert names == ["lookup_order", "check_refund_eligibility", "issue_refund"]
    assert transcript.resolution.status == "resolved"
    assert "O1001" in transcript.resolution.proposal


def test_underspecified_refund_escalates():
    agent = make_agent()
    transcript = agent.handle({"id": "R5", "intent": "refund"})
    assert transcript.resolution.status == "escalated"


def test_unknown_intent_escalates():
    agent = make_agent()
    transcript = agent.handle({"id": "R6", "intent": "complaint"})
    assert transcript.resolution.status == "escalated"


def test_ineligible_refund_lowers_completeness_and_escalates():
    # O1004 is cancelled: issue_refund fails, dragging completeness down.
    agent = make_agent()
    transcript = agent.handle(
        {"id": "R2", "intent": "refund", "order_id": "O1004"}
    )
    assert any(not c.ok for c in transcript.tool_calls)
    assert transcript.resolution.status == "escalated"
