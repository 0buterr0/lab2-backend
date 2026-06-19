"""Замовлення та його рядки. Тут зосереджена доменна модель 'замовлення'."""
from enum import Enum
from decimal import Decimal
from sqlalchemy import ForeignKey, Numeric, Integer, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..core.database import Base
from .base import TimestampMixin


class OrderStatus(str, Enum):
    """Машина станів замовлення: створене → оплачене / скасоване."""
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"


class Order(Base, TimestampMixin):
    """Заголовок замовлення. Сума total — кешований підсумок усіх рядків."""

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[OrderStatus] = mapped_column(SAEnum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)

    # Зворотні зв'язки: до якого клієнта належить, які рядки містить.
    client = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    def recalculate_total(self) -> Decimal:
        """Метод доменної моделі: перерахувати загальну суму на основі рядків замовлення."""
        total = sum((item.unit_price * item.quantity for item in self.items), Decimal("0.00"))
        self.total = total
        return total


class OrderItem(Base):
    """Один рядок замовлення: товар × кількість × ціна на момент покупки."""

    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    # RESTRICT — не дозволяємо видалити товар, якщо він уже в чиємусь замовленні.
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    # Ціну зберігаємо саме на момент покупки, щоб зміна ціни в каталозі не змінювала старі замовлення.
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product")
