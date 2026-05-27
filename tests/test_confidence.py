import pytest

from agentdesk.core.confidence import ConfidenceModel, score_confidence


def test_score_is_product_of_signal_and_completeness():
    assert score_confidence(0.8, 0.5) == 0.4
    assert score_confidence(1.0, 1.0) == 1.0


def test_score_rejects_out_of_range():
    with pytest.raises(ValueError):
        score_confidence(1.2, 0.5)
    with pytest.raises(ValueError):
        score_confidence(0.5, -0.1)


def test_threshold_must_be_in_range():
    with pytest.raises(ValueError):
        ConfidenceModel(1.5)


def test_decide_escalates_below_threshold():
    model = ConfidenceModel(0.7)
    confidence, escalate = model.decide(0.6, 1.0)
    assert confidence == 0.6
    assert escalate is True


def test_decide_resolves_at_threshold():
    model = ConfidenceModel(0.7)
    confidence, escalate = model.decide(0.7, 1.0)
    assert escalate is False
