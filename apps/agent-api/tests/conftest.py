import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from app.db import Base, get_db
from app.main import app

@pytest.fixture
def client():
    engine = create_engine("sqlite+pysqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    def override_db():
        with Session(engine) as db:
            yield db
    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as http:
        yield http
    app.dependency_overrides.clear()
    engine.dispose()
