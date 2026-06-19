"""Налаштування логування: одночасно в консоль і у файл з ротацією."""
import logging
import logging.handlers
from .config import settings


def setup_logging() -> None:
    """Викликається один раз при старті додатку (з main.py)."""
    root = logging.getLogger()
    if root.handlers:
        return  # уже налаштовано — захист від подвійної ініціалізації

    root.setLevel(settings.log_level)
    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Хендлер #1: вивід у консоль (зручно при розробці).
    console = logging.StreamHandler()
    console.setFormatter(fmt)
    root.addHandler(console)

    # Хендлер #2: запис у файл з ротацією (3 файли по ~2 МБ).
    file_handler = logging.handlers.RotatingFileHandler(
        settings.log_dir / "app.log",
        maxBytes=2_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(fmt)
    root.addHandler(file_handler)

    # Прибираємо шум від access-логів uvicorn.
    logging.getLogger("uvicorn.access").setLevel("WARNING")
