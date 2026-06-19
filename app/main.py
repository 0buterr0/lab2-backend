"""Точка входу backend-додатку.

Тут створюється об'єкт FastAPI, реєструються всі роутери (Front Controller),
налаштовуються CORS і обробник доменних помилок, виконується seed тестових даних.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .core.config import settings
from .core.logging import setup_logging
from .core.database import Base, engine
from .controllers import auth_router, product_router, order_router, blacklist_router
from .services.errors import ServiceError
from .bootstrap import seed


# Логування налаштовуємо одразу при імпорті модуля.
setup_logging()
log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Запускається один раз на старті/зупинці сервера. Тут створюємо схему БД і дані-seed."""
    log.info("Starting %s", settings.app_name)
    # Якщо не запускати Alembic вручну — таблиці створяться тут.
    Base.metadata.create_all(bind=engine)
    seed()  # додає admin/client/демо-товари при першому запуску
    yield
    log.info("Shutting down")


app = FastAPI(title=settings.app_name, lifespan=lifespan)

# CORS — дозволяємо запити з frontend dev-сервера (порт 5173).
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ServiceError)
async def service_error_handler(_: Request, exc: ServiceError) -> JSONResponse:
    """Усі доменні помилки (NotFound/Conflict/Forbidden/...) автоматично перетворюються на JSON."""
    return JSONResponse(status_code=exc.status_code, content={"detail": str(exc)})


# Підключаємо чотири контролери — це і є Front Controller / Route Patterns з методички.
app.include_router(auth_router)
app.include_router(product_router)
app.include_router(order_router)
app.include_router(blacklist_router)


@app.get("/")
def root() -> dict[str, str]:
    """Службовий маршрут — підтвердження, що API живий."""
    return {"app": settings.app_name, "docs": "/docs"}
