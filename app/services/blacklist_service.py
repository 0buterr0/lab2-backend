import logging
from sqlalchemy.orm import Session

from ..models.blacklist import BlacklistEntry
from ..repositories.blacklist_repository import BlacklistRepository
from ..repositories.user_repository import UserRepository
from .errors import NotFoundError, ConflictError

log = logging.getLogger(__name__)


class BlacklistService:
    def __init__(self, db: Session) -> None:
        self._repo = BlacklistRepository(db)
        self._users = UserRepository(db)

    def list(self) -> list[BlacklistEntry]:
        return list(self._repo.list())

    def add(self, user_id: int, reason: str = "non-payment") -> BlacklistEntry:
        user = self._users.get(user_id)
        if not user:
            raise NotFoundError(f"User {user_id} not found")
        if user.is_admin:
            raise ConflictError("Cannot blacklist an admin")
        if self._repo.get_by_user(user_id):
            raise ConflictError(f"User {user_id} is already blacklisted")
        entry = BlacklistEntry(user_id=user_id, reason=reason)
        self._repo.add(entry)
        self._repo.commit()
        log.info("Blacklisted user id=%s reason=%s", user_id, reason)
        return entry

    def remove(self, user_id: int) -> None:
        entry = self._repo.get_by_user(user_id)
        if not entry:
            raise NotFoundError(f"User {user_id} is not blacklisted")
        self._repo.delete(entry)
        self._repo.commit()
        log.info("Removed user id=%s from blacklist", user_id)
