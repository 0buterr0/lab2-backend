"""FastAPI-залежності для авторизації. Використовуються в контролерах через Depends(...)."""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.security import decode_token
from ..models.user import User, UserRole
from ..repositories.user_repository import UserRepository


# Очікуємо JWT у заголовку Authorization: Bearer <token>.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Витягнути користувача з JWT. 401, якщо токена немає / він зіпсований / користувача нема."""
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated",
                            headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = decode_token(token)
        user_id = int(payload["sub"])
    except (ValueError, KeyError):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token",
                            headers={"WWW-Authenticate": "Bearer"})
    user = UserRepository(db).get(user_id)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    """Захист адмінських ендпоінтів. Не-адмін отримає 403."""
    if user.role != UserRole.ADMIN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin role required")
    return user


def require_client(user: User = Depends(get_current_user)) -> User:
    """Захист клієнтських ендпоінтів (створення/оплата замовлень)."""
    if user.role != UserRole.CLIENT:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Client role required")
    return user
