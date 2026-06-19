"""Модель товару каталогу."""
from sqlalchemy import String, Numeric, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column
from decimal import Decimal
from ..core.database import Base
from .base import TimestampMixin


class Product(Base, TimestampMixin):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    # Numeric(10,2) — точно зберігаємо ціну, без помилок плаваючої коми.
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    # Залишок на складі. При оформленні замовлення зменшується, при скасуванні — повертається.
    stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
