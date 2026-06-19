"""Безпека: хешування паролів (bcrypt) та видача/перевірка JWT-токенів."""
from datetime import datetime, timedelta, timezone
from typing import Any
import bcrypt
from jose import jwt, JWTError
from .config import settings


# bcrypt має жорсткий ліміт 72 байти на пароль — обрізаємо, щоб не падало.
def _to_bytes(plain: str) -> bytes:
    return plain.encode("utf-8")[:72]


def hash_password(plain: str) -> str:
    """Згенерувати bcrypt-хеш для збереження в БД (зі своєю сіллю)."""
    return bcrypt.hashpw(_to_bytes(plain), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Звірити введений пароль з хешем у БД (порівняння в постійному часі)."""
    try:
        return bcrypt.checkpw(_to_bytes(plain), hashed.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(subject: str, extra: dict[str, Any] | None = None) -> str:
    """Створити JWT для користувача.

    sub — ідентифікатор користувача; iat/exp — часові мітки; extra — додаткові claims (роль, ім'я).
    Підписується HS256 з секретом із налаштувань.
    """
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.jwt_expire_minutes)).timestamp()),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any]:
    """Перевірити підпис JWT і повернути його payload. Кидає ValueError при невалідному/протермінованому токені."""
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise ValueError("Invalid or expired token") from exc
