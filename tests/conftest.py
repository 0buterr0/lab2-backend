import os
import tempfile
from collections.abc import Iterator

# Use an isolated SQLite file per test session BEFORE importing app modules.
_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp.close()
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp.name}"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

# Patch settings before importing the app.
from app.core import config as _cfg  # noqa: E402
_cfg.settings.database_url = os.environ["DATABASE_URL"]

from app.core import database as _db  # noqa: E402
_db.engine = create_engine(_cfg.settings.database_url, connect_args={"check_same_thread": False}, future=True)
_db.SessionLocal = sessionmaker(bind=_db.engine, autoflush=False, autocommit=False, expire_on_commit=False)

from app.core.database import Base, engine, SessionLocal  # noqa: E402
from app import models  # noqa: F401,E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _create_schema() -> Iterator[None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    try:
        os.unlink(_tmp.name)
    except OSError:
        pass


@pytest.fixture()
def db():
    s = SessionLocal()
    try:
        yield s
    finally:
        s.close()


@pytest.fixture()
def client() -> Iterator[TestClient]:
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def admin_token(client: TestClient) -> str:
    r = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


@pytest.fixture()
def client_token(client: TestClient) -> str:
    r = client.post("/api/auth/login", json={"username": "client", "password": "client123"})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}
