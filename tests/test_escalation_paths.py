"""The escalation paths the agent must take.

Each case is a request and whether the agent should resolve it on its own or
hand it to a human, given the default threshold.
"""

import pytest

from agentdesk.backend import Backend
from agentdesk.core import Agent
from agentdesk.provider import FakeProvider
from agentdesk.tools import build_registry


def run(request):
    agent = Agent(build_registry(Backend()), FakeProvider())
    return agent.handle(request)


@pytest.mark.parametrize(
    "request_,expected",
    [
        ({"id": "a", "intent": "refund", "order_id": "O1001"}, "resolved"),
        ({"id": "b", "intent": "address", "account_id": "A100", "address": "1 New Rd"}, "resolved"),
        ({"id": "c", "intent": "account_status", "account_id": "A200"}, "resolved"),
        ({"id": "d", "intent": "refund", "order_id": "O1004"}, "escalated"),
        ({"id": "e", "intent": "refund"}, "escalated"),
        ({"id": "f", "intent": "complaint"}, "escalated"),
        ({"id": "g", "intent": "address", "account_id": "A100"}, "escalated"),
    ],
)
def test_request_takes_expected_path(request_, expected):
    transcript = run(request_)
    assert transcript.resolution is not None
    assert transcript.resolution.status == expected


def test_escalated_request_has_no_proposed_action():
    transcript = run({"id": "h", "intent": "complaint"})
    assert transcript.resolution.proposal == ""


def test_failed_tool_call_does_not_crash_the_loop():
    # the ineligible refund path runs issue_refund, which fails; the loop
    # must still return a transcript with the failure recorded.
    transcript = run({"id": "i", "intent": "refund", "order_id": "O1004"})
    assert any(call.error for call in transcript.tool_calls)
    assert transcript.resolution is not None
