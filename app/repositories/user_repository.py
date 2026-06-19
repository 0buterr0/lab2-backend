"""Репозиторій користувачів. Наслідує всі CRUD-операції від BaseRepository[User]."""
from sqlalchemy import select
from .base import BaseRepository
from ..models.user import User


class UserRepository(BaseRepository[User]):
    model = User

    # Специфічний метод, якого немає в базовому класі — пошук за унікальним логіном.
    def get_by_username(self, username: str) -> User | None:
        return self._db.scalar(select(User).where(User.username == username))
