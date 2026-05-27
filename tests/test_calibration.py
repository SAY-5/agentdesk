"""Decision-table test for the confidence model.

This is the differentiator: it pins down exactly when the agent acts on its own
and when it hands off. The table lists a provider signal, the tool-call
completeness, the resulting confidence (signal times completeness), and the
expected decision at the default threshold. It then shows that moving the
threshold moves the auto-resolve boundary as expected.
"""

import pytest

from agentdesk.core.confidence import ConfidenceModel, score_confidence

# signal, completeness, expected confidence, escalate at threshold 0.7
DECISION_TABLE = [
    (1.0, 1.0, 1.0, False),   # strong signal, every tool succeeded: act
    (0.9, 1.0, 0.9, False),   # high signal, complete: act
    (0.7, 1.0, 0.7, False),   # exactly at the threshold: act
    (0.69, 1.0, 0.69, True),  # just under the threshold: hand off
    (0.9, 0.5, 0.45, True),   # high signal but half the tools failed: hand off
    (0.2, 1.0, 0.2, True),    # low signal, complete: hand off
    (0.5, 0.5, 0.25, True),   # weak on both: hand off
]


@pytest.mark.parametrize("signal,completeness,confidence,escalate", DECISION_TABLE)
def test_decision_table_at_default_threshold(signal, completeness, confidence, escalate):
    model = ConfidenceModel(0.7)
    score = score_confidence(signal, completeness)
    assert score == confidence
    assert model.should_escalate(score) is escalate


def test_high_confidence_request_is_auto_resolved():
    model = ConfidenceModel(0.7)
    score, escalate = model.decide(signal=0.9, completeness=1.0)
    assert score == 0.9
    assert escalate is False


def test_ambiguous_low_signal_request_escalates():
    model = ConfidenceModel(0.7)
    score, escalate = model.decide(signal=0.3, completeness=1.0)
    assert escalate is True


def test_a_single_failed_tool_call_can_force_a_handoff():
    # completeness 0.5 means one of two tool calls failed
    model = ConfidenceModel(0.7)
    _, escalate = model.decide(signal=0.95, completeness=0.5)
    assert escalate is True


def test_lowering_the_threshold_moves_the_boundary():
    # a request scoring 0.5 escalates at the default but auto-resolves once the
    # operator lowers the threshold below it.
    score = score_confidence(0.5, 1.0)
    assert ConfidenceModel(0.7).should_escalate(score) is True
    assert ConfidenceModel(0.4).should_escalate(score) is False


def test_raising_the_threshold_makes_the_agent_more_cautious():
    score = score_confidence(0.8, 1.0)
    assert ConfidenceModel(0.7).should_escalate(score) is False
    assert ConfidenceModel(0.9).should_escalate(score) is True
