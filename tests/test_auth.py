from fastapi.testclient import TestClient
from sqlalchemy import select
from ecommerceapi.models.user import User

from tests.factories.user_factory import UserFactory


def test_register_success(test_client: TestClient) -> None:
    payload = {
        "email": "user1@test.com",
        "password": "password123",
        "first_name": "Hanna",
        "last_name": "Kirieieva",
        "address": {
            "city": "Warsaw",
            "region": None,
            "postal_code": "00-001",
            "country": "PL",
        },
    }
    resp = test_client.post("/auth/register", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    assert data["email"] == "user1@test.com"


def test_login_returns_tokens(
    test_client: TestClient, db_test_session, user_factory: UserFactory
):
    # password is password123
    u = user_factory.create()

    resp = test_client.post(
        "/auth/login", data={"username": u.email, "password": "password123"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_refresh_rotates_refresh_token(
    test_client: TestClient, db_test_session, user_factory: UserFactory
):
    u = user_factory.create()

    login = test_client.post(
        "/auth/login", data={"username": u.email, "password": "password123"}
    )
    assert login.status_code == 200
    tokens = login.json()
    old_refresh = tokens["refresh_token"]

    resp = test_client.post("/auth/refresh", params={"refresh_token": old_refresh})
    assert resp.status_code == 200
    new_tokens = resp.json()
    assert new_tokens["refresh_token"] != old_refresh


def test_logout_revokes_refresh_token(
    test_client: TestClient, user_factory: UserFactory
):
    u = user_factory.create()

    login = test_client.post(
        "/auth/login", data={"username": u.email, "password": "password123"}
    )
    assert login.status_code == 200
    refresh = login.json()["refresh_token"]

    out = test_client.post("/auth/logout", params={"refresh_token": refresh})
    assert out.status_code == 200
    assert out.json()["message"] == "ok"


def test_register_rolls_back_if_address_create_fails(
    test_client: TestClient, db_test_session, monkeypatch
):
    # raises exception because country is limited to 2 chars.
    payload = {
        "email": "rollback@test.com",
        "password": "password123",
        "first_name": "Hanna",
        "last_name": "Kirieieva",
        "address": {
            "city": "Warsaw",
            "region": None,
            "postal_code": "00-001",
            "country": "POL",
        },
    }

    resp = test_client.post("/auth/register", json=payload)
    assert resp.status_code == 422

    user = (
        db_test_session.execute(select(User).where(User.email == "rollback@test.com"))
        .scalars()
        .first()
    )

    assert user is None
