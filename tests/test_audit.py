"""Audit trail and human-in-loop replay.

Proves that an escalated request keeps a full transcript, that a human can
replay it, and that approving or overriding it completes the request with the
decision recorded in the trail.
"""

import pytest

from agentdesk.audit import AuditError
from agentdesk.service import Service


def submit_escalation(service):
    # an unknown intent always escalates
    service.submit({"id": "E1", "intent": "complaint", "text": "I want a person"})
    return "E1"


def test_transcript_captures_the_full_trace():
    service = Service()
    service.submit({"id": "R1", "intent": "refund", "order_id": "O1001"})
    transcript = service.transcript("R1")
    assert [c["name"] for c in transcript["tool_calls"]] == [
        "lookup_order",
        "check_refund_eligibility",
        "issue_refund",
    ]
    assert len(transcript["provider_signals"]) >= 1
    assert transcript["resolution"]["status"] == "resolved"


def test_human_can_replay_an_escalation():
    service = Service()
    rid = submit_escalation(service)
    escalations = service.escalations()
    assert any(e["request_id"] == rid for e in escalations)


def test_replay_returns_the_stored_transcript():
    from agentdesk.audit import AuditTrail
    from agentdesk.core.result import Resolution, Transcript

    trail = AuditTrail()
    transcript = Transcript(request_id="Z1", request={"intent": "complaint"})
    transcript.resolution = Resolution("Z1", "escalated", "", 0.2, "below threshold")
    trail.record(transcript)

    replayed = trail.replay("Z1")
    assert replayed["request_id"] == "Z1"
    assert replayed["resolution"]["status"] == "escalated"
    with pytest.raises(AuditError):
        trail.replay("nope")


def test_approving_an_escalation_completes_it_and_records_the_decision():
    service = Service()
    rid = submit_escalation(service)

    result = service.resolve_escalation(rid, "approve", "")

    assert result["resolution"]["status"] == "resolved"
    assert result["human_decision"]["decision"] == "approve"
    # the decision is persisted in the trail, not just returned
    stored = service.transcript(rid)
    assert stored["human_decision"]["decision"] == "approve"
    assert stored["resolution"]["status"] == "resolved"


def test_overriding_records_the_human_note():
    service = Service()
    rid = submit_escalation(service)

    result = service.resolve_escalation(rid, "override", "issued goodwill credit")

    assert result["human_decision"]["decision"] == "override"
    assert result["resolution"]["proposal"] == "issued goodwill credit"
    assert service.transcript(rid)["human_decision"]["note"] == "issued goodwill credit"


def test_cannot_decide_on_a_resolved_request():
    service = Service()
    service.submit({"id": "R1", "intent": "refund", "order_id": "O1001"})
    with pytest.raises(AuditError):
        service.resolve_escalation("R1", "approve", "")


def test_unknown_decision_is_rejected():
    service = Service()
    rid = submit_escalation(service)
    with pytest.raises(AuditError):
        service.resolve_escalation(rid, "maybe", "")


def test_decision_on_unknown_request_is_rejected():
    service = Service()
    with pytest.raises(AuditError):
        service.resolve_escalation("missing", "approve", "")
