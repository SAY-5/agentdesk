from agentdesk.service import Service


def test_submit_records_in_queue():
    service = Service()
    service.submit({"id": "R1", "intent": "refund", "order_id": "O1001"})
    service.submit({"id": "R6", "intent": "complaint"})
    assert len(service.queue()) == 2
    assert len(service.escalations()) == 1


def test_transcript_lookup():
    service = Service()
    service.submit({"id": "R4", "intent": "account_status", "account_id": "A200"})
    found = service.transcript("R4")
    assert found is not None
    assert found["request_id"] == "R4"
    assert service.transcript("missing") is None
