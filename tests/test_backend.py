import pytest

from agentdesk.backend import Backend, BackendError


def test_lookup_order_returns_fields():
    backend = Backend()
    order = backend.lookup_order("O1001")
    assert order["account_id"] == "A100"
    assert order["status"] == "delivered"


def test_unknown_order_raises():
    backend = Backend()
    with pytest.raises(BackendError):
        backend.lookup_order("nope")


def test_refund_eligible_order_can_be_issued():
    backend = Backend()
    assert backend.check_refund_eligibility("O1001")["eligible"] is True
    refund = backend.issue_refund("O1001")
    assert refund["refunded"] == 49.99
    # second refund on the same order is rejected
    assert backend.check_refund_eligibility("O1001")["eligible"] is False
    with pytest.raises(BackendError):
        backend.issue_refund("O1001")


def test_cancelled_order_is_not_refundable():
    backend = Backend()
    assert backend.check_refund_eligibility("O1004")["eligible"] is False


def test_update_address_rejects_empty():
    backend = Backend()
    with pytest.raises(BackendError):
        backend.update_address("A100", "  ")
