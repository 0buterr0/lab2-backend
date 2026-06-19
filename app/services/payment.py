"""Платіжна система — наочний приклад поліморфізму (Strategy pattern).

OrderService приймає будь-який об'єкт типу PaymentProcessor і викликає charge() —
конкретна реалізація вирішує, як проводиться оплата (тестова, реальна, відмова тощо).
"""
import logging
from abc import ABC, abstractmethod
from decimal import Decimal

log = logging.getLogger(__name__)


class PaymentProcessor(ABC):
    """Абстрактний клас (інтерфейс) платіжного процесора.

    ABC + @abstractmethod забороняють створити екземпляр самого PaymentProcessor —
    обов'язково треба реалізувати charge() у нащадку.
    """

    @abstractmethod
    def charge(self, *, order_id: int, amount: Decimal) -> bool: ...


class MockPaymentProcessor(PaymentProcessor):
    """Заглушка для розробки і e2e — завжди підтверджує оплату."""

    def charge(self, *, order_id: int, amount: Decimal) -> bool:
        log.info("MockPaymentProcessor: charging order=%s amount=%s", order_id, amount)
        return True


class AlwaysFailingProcessor(PaymentProcessor):
    """Реалізація для unit-тестів — імітує відмову банку.

    Завдяки поліморфізму OrderService без жодних змін реагує на відмову,
    хоча в основному режимі він працює з MockPaymentProcessor.
    """

    def charge(self, *, order_id: int, amount: Decimal) -> bool:
        log.warning("AlwaysFailingProcessor: refused order=%s amount=%s", order_id, amount)
        return False
