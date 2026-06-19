"""Налаштування додатку. Зчитуються з .env або беруться зі значень за замовчуванням."""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Усі налаштування зібрані в один pydantic-клас (типобезпечно)."""

    app_name: str = "Internet Store API"
    debug: bool = True

    # Підключення до БД (за замовчуванням — локальний SQLite-файл).
    database_url: str = f"sqlite:///{BASE_DIR / 'data' / 'store.db'}"

    # Параметри JWT: секрет, алгоритм підпису, термін життя токена.
    jwt_secret: str = "change-me-in-production-please-very-long-random-string"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 8

    # Список джерел, яким дозволено робити CORS-запити (frontend dev-сервер).
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # Куди писати логи і з яким рівнем.
    log_dir: Path = BASE_DIR / "logs"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
settings.log_dir.mkdir(parents=True, exist_ok=True)
(BASE_DIR / "data").mkdir(parents=True, exist_ok=True)
