import logging
from sqlalchemy.orm import Session

from ..core.security import hash_password, verify_password, create_access_token
from ..models.user import User, UserRole
from ..repositories.user_repository import UserRepository
from .errors import AuthError, ConflictError

log = logging.getLogger(__name__)


class AuthService:
    def __init__(self, db: Session) -> None:
        self._users = UserRepository(db)

    def register(self, *, username: str, password: str, full_name: str = "",
                 role: UserRole = UserRole.CLIENT) -> User:
        if self._users.get_by_username(username):
            raise ConflictError(f"Username '{username}' already taken")
        user = User(
            username=username,
            password_hash=hash_password(password),
            full_name=full_name,
            role=role,
        )
        self._users.add(user)
        self._users.commit()
        log.info("Registered user id=%s username=%s role=%s", user.id, user.username, user.role.value)
        return user

    def authenticate(self, *, username: str, password: str) -> tuple[User, str]:
        user = self._users.get_by_username(username)
        if not user or not verify_password(password, user.password_hash):
            log.warning("Auth failed for username=%s", username)
            raise AuthError("Invalid credentials")
        token = create_access_token(
            subject=str(user.id),
            extra={"role": user.role.value, "username": user.username},
        )
        log.info("Auth success user id=%s username=%s", user.id, user.username)
        return user, token
