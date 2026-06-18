import logging
from abc import ABC, abstractmethod
from decimal import Decimal

log = logging.getLogger(__name__)


class PaymentProcessor(ABC):
    """Strategy/Template — concrete processors implement charge().

    Demonstrates polymorphism: OrderService accepts any subclass.
    """

    @abstractmethod
    def charge(self, *, order_id: int, amount: Decimal) -> bool: ...


class MockPaymentProcessor(PaymentProcessor):
    """Always succeeds. Useful for local dev & tests."""

    def charge(self, *, order_id: int, amount: Decimal) -> bool:
        log.info("MockPaymentProcessor: charging order=%s amount=%s", order_id, amount)
        return True


class AlwaysFailingProcessor(PaymentProcessor):
    """Used in tests to simulate refused payments."""

    def charge(self, *, order_id: int, amount: Decimal) -> bool:
        log.warning("AlwaysFailingProcessor: refused order=%s amount=%s", order_id, amount)
        return False
