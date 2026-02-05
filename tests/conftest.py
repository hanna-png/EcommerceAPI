import os
import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy_utils import create_database, database_exists, drop_database

from ecommerceapi.db.database import get_db
from ecommerceapi.main import app
from tests.factories.category_factory import CategoryFactory
from tests.factories.product_factory import ProductFactory
from tests.factories.user_factory import UserFactory


DATABASE_URL_TEST = os.getenv("DATABASE_URL_TEST")
if not DATABASE_URL_TEST:
    raise RuntimeError("DATABASE_URL_TEST is not set")


def _admin_url() -> str:
    """
    Reuse DATABASE_URL_TEST credentials/host/port, but connect to the 'postgres' DB.
    """
    url = make_url(DATABASE_URL_TEST)
    return url.set(database="postgres").render_as_string(hide_password=False)


@pytest.fixture(scope="session", autouse=True)
def test_database_lifecycle():
    """
    Create test database, apply migrations, close all the connections and drop the db.
    """
    test_url = make_url(DATABASE_URL_TEST)

    if not database_exists(test_url):
        create_database(test_url)

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", DATABASE_URL_TEST)
    command.upgrade(alembic_cfg, "head")

    yield
    terminate_background_processes(test_url)
    drop_database(test_url)


def terminate_background_processes(test_url):
    admin_engine = create_engine(
        _admin_url(), isolation_level="AUTOCOMMIT", poolclass=NullPool
    )
    try:
        with admin_engine.connect() as conn:
            conn.execute(
                text(
                    """
                    SELECT pg_terminate_backend(pid)
                    FROM pg_stat_activity
                    WHERE datname = :name AND pid <> pg_backend_pid()
                    """
                ),
                {"name": test_url.database},
            )
    finally:
        admin_engine.dispose()


@pytest.fixture(scope="session")
def engine_test(test_database_lifecycle: None):
    """One SQLAlchemy Engine for the whole test session."""
    engine = create_engine(DATABASE_URL_TEST, poolclass=NullPool)
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture(scope="session")
def test_session_factory(engine_test: Engine):
    """A sessionmaker bound to the test engine."""
    return sessionmaker(bind=engine_test, autoflush=False, expire_on_commit=False)


@pytest.fixture()
def db_test_session(test_session_factory: sessionmaker, engine_test: Engine):
    """
    Create one SQLAlchemy Session per test.
    """
    connection = engine_test.connect()
    transaction = connection.begin()
    session: Session = test_session_factory(bind=connection)

    try:
        yield session
    finally:
        session.close()
        if transaction.is_active:
            transaction.rollback()
        connection.close()


@pytest.fixture()
def test_client(db_test_session):
    """Create FastAPI TestClient"""

    def override_get_db():
        nested = db_test_session.begin_nested()
        try:
            yield db_test_session
            nested.commit()
        except Exception:
            nested.rollback()
            raise

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            yield client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture()
def category_factory(db_test_session):
    CategoryFactory._meta.sqlalchemy_session = db_test_session
    return CategoryFactory


@pytest.fixture()
def product_factory(db_test_session):
    ProductFactory._meta.sqlalchemy_session = db_test_session
    return ProductFactory


@pytest.fixture()
def user_factory(db_test_session):
    UserFactory._meta.sqlalchemy_session = db_test_session
    return UserFactory


@pytest.fixture()
def test_access_token(test_client: TestClient, user_factory):
    u = user_factory.create()
    resp = test_client.post(
        "/auth/login",
        data={"username": u.email, "password": "password123"},
    )
    assert resp.status_code == 200, resp.json()
    access = resp.json()["access_token"]
    return {"Authorization": f"Bearer {access}"}
