"""Підключення до БД через SQLAlchemy ORM. Один engine + фабрика сесій на весь додаток."""
from typing import Iterator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from .config import settings


# SQLite потребує спеціального прапорця, бо FastAPI може використовувати кілька потоків.
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

# Engine — основне підключення до БД (пул з'єднань).
engine = create_engine(settings.database_url, connect_args=connect_args, future=True)

# Фабрика сесій. Кожен HTTP-запит отримує власну сесію через get_db().
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Базовий клас для всіх ORM-моделей. Від нього успадковуються User, Product, Order тощо."""


def get_db() -> Iterator[Session]:
    """FastAPI-залежність: відкриває сесію на час запиту і гарантовано закриває її в кінці."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
