import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ВАЖНО: до импорта app.* подменяем DATABASE_URL на sqlite in-memory
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from app.database import Base, get_db          # noqa: E402
from app.main import app                        # noqa: E402
from app import models                          # noqa: E402
from app.security import hash_password          # noqa: E402


@pytest.fixture(scope="session")
def engine():
    engine = create_engine(
        "sqlite:///./test.db",
        connect_args={"check_same_thread": False},
    )
    yield engine
    engine.dispose()
    if os.path.exists("test.db"):
        os.remove("test.db")


@pytest.fixture(scope="session")
def TestingSessionLocal(engine):
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture(autouse=True)
def setup_db(engine, TestingSessionLocal):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        user = models.User(
            username="alice",
            email="alice@example.com",
            password_hash=hash_password("secret123"),
        )
        db.add(user)
        db.commit()
    finally:
        db.close()

    yield


@pytest.fixture
def client(TestingSessionLocal):
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    r = client.post(
        "/auth/login",
        json={"username": "alice", "email": "alice@example.com", "password": "secret123"},
    )
    assert r.status_code == 200, r.text
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
