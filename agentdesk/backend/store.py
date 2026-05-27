"""In-memory mock backend for customer operations.

This stands in for a real order/account system. It holds a small set of
accounts and orders and exposes plain methods that the tool layer wraps.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from datetime import date


class BackendError(Exception):
    """Raised when a backend operation cannot be completed."""


@dataclass
class Order:
    order_id: str
    account_id: str
    status: str
    total: float
    placed_on: str
    refundable: bool


@dataclass
class Account:
    account_id: str
    name: str
    email: str
    address: str
    orders: list[str] = field(default_factory=list)


def _seed_accounts() -> dict[str, Account]:
    return {
        "A100": Account("A100", "Dana Reyes", "dana@example.com", "12 Oak St, Portland OR"),
        "A200": Account("A200", "Sam Cole", "sam@example.com", "9 Pine Ave, Austin TX"),
        "A300": Account("A300", "Lee Park", "lee@example.com", "55 Elm Rd, Denver CO"),
    }


def _seed_orders() -> dict[str, Order]:
    return {
        "O1001": Order("O1001", "A100", "delivered", 49.99, "2026-04-02", True),
        "O1002": Order("O1002", "A100", "shipped", 18.50, "2026-05-10", False),
        "O1003": Order("O1003", "A200", "delivered", 120.00, "2026-03-15", True),
        "O1004": Order("O1004", "A300", "cancelled", 75.25, "2026-05-01", False),
    }


class Backend:
    """A small mutable store with deterministic seed data."""

    def __init__(self) -> None:
        self._accounts = _seed_accounts()
        self._orders = _seed_orders()
        for order in self._orders.values():
            self._accounts[order.account_id].orders.append(order.order_id)
        self._refunds: dict[str, float] = {}

    def get_account(self, account_id: str) -> dict:
        account = self._accounts.get(account_id)
        if account is None:
            raise BackendError(f"unknown account {account_id}")
        return {
            "account_id": account.account_id,
            "name": account.name,
            "email": account.email,
            "address": account.address,
            "orders": list(account.orders),
        }

    def lookup_order(self, order_id: str) -> dict:
        order = self._orders.get(order_id)
        if order is None:
            raise BackendError(f"unknown order {order_id}")
        return {
            "order_id": order.order_id,
            "account_id": order.account_id,
            "status": order.status,
            "total": order.total,
            "placed_on": order.placed_on,
            "refundable": order.refundable,
        }

    def check_refund_eligibility(self, order_id: str) -> dict:
        order = self._orders.get(order_id)
        if order is None:
            raise BackendError(f"unknown order {order_id}")
        already = order.order_id in self._refunds
        eligible = order.refundable and order.status == "delivered" and not already
        reason = "eligible"
        if already:
            reason = "already refunded"
        elif not order.refundable:
            reason = "order marked non-refundable"
        elif order.status != "delivered":
            reason = f"status is {order.status}"
        return {"order_id": order.order_id, "eligible": eligible, "reason": reason}

    def issue_refund(self, order_id: str) -> dict:
        order = self._orders.get(order_id)
        if order is None:
            raise BackendError(f"unknown order {order_id}")
        eligibility = self.check_refund_eligibility(order_id)
        if not eligibility["eligible"]:
            raise BackendError(f"refund rejected: {eligibility['reason']}")
        self._refunds[order_id] = order.total
        return {"order_id": order.order_id, "refunded": order.total, "status": "refunded"}

    def update_address(self, account_id: str, address: str) -> dict:
        account = self._accounts.get(account_id)
        if account is None:
            raise BackendError(f"unknown account {account_id}")
        if not address.strip():
            raise BackendError("address cannot be empty")
        account.address = address
        return {"account_id": account.account_id, "address": account.address}

    def snapshot(self) -> dict:
        """Return a deep copy of state, used by the audit layer for replay."""
        return {
            "accounts": copy.deepcopy(self._accounts),
            "orders": copy.deepcopy(self._orders),
            "refunds": dict(self._refunds),
        }

    @property
    def today(self) -> str:
        return date(2026, 5, 27).isoformat()
