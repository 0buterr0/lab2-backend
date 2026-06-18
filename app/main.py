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


setup_logging()
log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Starting %s", settings.app_name)
    # If you don't use Alembic at runtime, create tables; otherwise use `alembic upgrade head`.
    Base.metadata.create_all(bind=engine)
    seed()
    yield
    log.info("Shutting down")


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ServiceError)
async def service_error_handler(_: Request, exc: ServiceError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": str(exc)})


app.include_router(auth_router)
app.include_router(product_router)
app.include_router(order_router)
app.include_router(blacklist_router)


@app.get("/")
def root() -> dict[str, str]:
    return {"app": settings.app_name, "docs": "/docs"}
