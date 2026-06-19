"""Модель користувача (доменна сутність 'User')."""
from enum import Enum
from sqlalchemy import String, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..core.database import Base
from .base import TimestampMixin


class UserRole(str, Enum):
    """Дві ролі за умовою лаби: адміністратор і клієнт."""
    ADMIN = "admin"
    CLIENT = "client"


# Множинне наслідування: Base (ORM) + TimestampMixin (created_at/updated_at).
class User(Base, TimestampMixin):
    __tablename__ = "users"

    # --- Колонки таблиці users ---
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)  # bcrypt-хеш, не сам пароль
    full_name: Mapped[str] = mapped_column(String(128), default="")
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), default=UserRole.CLIENT, nullable=False)

    # --- Зв'язки з іншими таблицями ---
    # Один користувач -> багато замовлень. Видалення користувача каскадно видаляє його замовлення.
    orders = relationship("Order", back_populates="client", cascade="all, delete-orphan")
    # Один-до-одного з blacklist (uselist=False). Якщо запис є — користувача занесено в чорний список.
    blacklist_entry = relationship(
        "BlacklistEntry",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    # --- Зручні похідні властивості (інкапсуляція логіки 'роль/чорний список') ---
    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN

    @property
    def is_blacklisted(self) -> bool:
        return self.blacklist_entry is not None
