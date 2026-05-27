"""A fixed set of inbound requests used by the demo and the benchmark."""

from __future__ import annotations

from typing import Any

SAMPLE_REQUESTS: list[dict[str, Any]] = [
    {"id": "R1", "intent": "refund", "order_id": "O1001", "text": "Please refund my order."},
    {"id": "R2", "intent": "refund", "order_id": "O1004", "text": "I want my money back."},
    {"id": "R3", "intent": "address", "account_id": "A100", "address": "100 New St, Reno NV"},
    {"id": "R4", "intent": "account_status", "account_id": "A200"},
    {"id": "R5", "intent": "refund", "text": "refund please"},
    {"id": "R6", "intent": "complaint", "text": "this is unacceptable, I want to talk to someone"},
]
