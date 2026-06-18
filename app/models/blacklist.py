from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..core.database import Base
from .base import TimestampMixin


class BlacklistEntry(Base, TimestampMixin):
    __tablename__ = "blacklist"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    reason: Mapped[str] = mapped_column(String(255), default="non-payment")

    user = relationship("User", back_populates="blacklist_entry")
