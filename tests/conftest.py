import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from fastapi.testclient import TestClient

from ecommerceapi.main import app
from ecommerceapi.db.database import get_db

DATABASE_URL_TEST = os.getenv("DATABASE_URL_TEST")
if not DATABASE_URL_TEST:
    raise RuntimeError("DATABASE_URL_TEST not set")

engine_test = create_engine(DATABASE_URL_TEST, poolclass=NullPool)

TestSession = sessionmaker(bind=engine_test, autoflush=False, expire_on_commit=False)


@pytest.fixture()
def db_test_session():
    """
    Manages one session per test(function).
    """
    connection = engine_test.connect()
    transaction = connection.begin()
    session = TestSession(bind=connection)

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture()
def test_client(db_test_session: Session):
    """
    Create a TestClient that uses the test database session.
    """

    def override_get_db():
        """
        Overrides default get_db dependency (which is used by API endpoints)
        to a test one.
        """
        yield db_test_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.clear()
