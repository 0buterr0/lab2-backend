"""Спільні mixin-и для моделей."""
from datetime import datetime, timezone
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TimestampMixin:
    """ООП — наслідування через mixin.

    Будь-яка модель, що успадковує TimestampMixin, автоматично отримує колонки
    created_at / updated_at без дублювання коду (DRY).
    """

    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=_utcnow, onupdate=_utcnow, nullable=False
    )
