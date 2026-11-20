import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.session import Base, get_db
import app.database.models  # Ensure all models are registered on Base.metadata
from app.main import app
from app.database.seed import seed_database
from app.services.auth_service import create_access_token

TEST_DB_FILE = Path(__file__).parent / "test_suite.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{TEST_DB_FILE}"

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    if TEST_DB_FILE.exists():
        try:
            TEST_DB_FILE.unlink()
        except Exception:
            pass
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    seed_database(db)
    db.close()
    yield
    if TEST_DB_FILE.exists():
        try:
            TEST_DB_FILE.unlink()
        except Exception:
            pass

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def test_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def demo1_auth_headers():
    token = create_access_token({"sub": "s-demo-001", "email": "demo1@example.com"})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def demo2_auth_headers():
    token = create_access_token({"sub": "s-demo-002", "email": "demo2@example.com"})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def demo3_auth_headers():
    token = create_access_token({"sub": "s-demo-003", "email": "demo3@example.com"})
    return {"Authorization": f"Bearer {token}"}
