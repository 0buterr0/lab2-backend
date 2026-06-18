from sqlalchemy import select
from .base import BaseRepository
from ..models.user import User


class UserRepository(BaseRepository[User]):
    model = User

    def get_by_username(self, username: str) -> User | None:
        return self._db.scalar(select(User).where(User.username == username))
