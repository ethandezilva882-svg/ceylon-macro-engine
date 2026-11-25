import os

from dotenv import load_dotenv

load_dotenv()

# Point everything at the test DB BEFORE any Backend import creates the engine.
_base_url = os.environ["DATABASE_URL"]
os.environ["DATABASE_URL"] = _base_url.rsplit("/", 1)[0] + "/ceylon_test"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from Backend.database import engine, Base, SessionLocal
from Backend import models  # noqa: F401  (registers tables on Base)
from Backend.main import app

assert engine.url.database == "ceylon_test", "Refusing to run tests against a non-test DB"


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture(autouse=True)
def clean_db():
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE users, baskets, inflation_data RESTART IDENTITY CASCADE"))
    yield


@pytest.fixture
def client():
    # No `with` block, so the lifespan (scheduler) does not start during tests.
    return TestClient(app)


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def auth_headers(client):
    res = client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "password": "testpassword123"},
    )
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
