"""Репозиторій чорного списку."""
from sqlalchemy import select
from .base import BaseRepository
from ..models.blacklist import BlacklistEntry


class BlacklistRepository(BaseRepository[BlacklistEntry]):
    model = BlacklistEntry

    def get_by_user(self, user_id: int) -> BlacklistEntry | None:
        """Перевірити, чи є запис у чорному списку для конкретного користувача."""
        return self._db.scalar(select(BlacklistEntry).where(BlacklistEntry.user_id == user_id))
