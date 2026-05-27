"""The threshold changes behavior through the whole agent loop, not just in the
confidence helper. The same request resolves under a permissive threshold and
escalates under a stricter one.
"""

from agentdesk.backend import Backend
from agentdesk.core import Agent
from agentdesk.core.confidence import ConfidenceModel
from agentdesk.provider import FakeProvider
from agentdesk.tools import build_registry


def run_with_threshold(request, threshold):
    agent = Agent(build_registry(Backend()), FakeProvider(), ConfidenceModel(threshold))
    return agent.handle(request)


def test_account_status_resolves_at_default_but_escalates_when_strict():
    # account_status finalizes with signal 0.88 and full completeness.
    request = {"id": "t1", "intent": "account_status", "account_id": "A200"}

    resolved = run_with_threshold(request, 0.7)
    assert resolved.resolution.status == "resolved"
    assert resolved.resolution.confidence == 0.88

    strict = run_with_threshold(request, 0.95)
    assert strict.resolution.status == "escalated"
