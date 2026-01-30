from fastapi.testclient import TestClient
from sqlalchemy import select

from ecommerceapi.repositories.refresh_token import RefreshTokenRepository
from ecommerceapi.models.user import User
from ecommerceapi.models.refresh_token import RefreshToken
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
    assert resp.status_code == 500

    user = (
        db_test_session.execute(select(User).where(User.email == "rollback@test.com"))
        .scalars()
        .first()
    )

    assert user is None


def test_login_invalid_credentials_returns_401(test_client):
    resp = test_client.post(
        "/auth/login",
        data={"username": "missing@test.com", "password": "wrong"},
    )
    assert resp.status_code == 401
    assert resp.json()["detail"]


def test_get_missing_resource_returns_404(test_client):
    resp = test_client.get("/products/999999")
    assert resp.status_code == 404
    assert resp.json()["detail"]


def test_refresh_does_not_revoke_old_token_if_create_fails(
    test_client, db_test_session, user_factory, monkeypatch
):
    u = user_factory.create()
    login = test_client.post(
        "/auth/login", data={"username": u.email, "password": "password123"}
    )
    assert login.status_code == 200
    old_refresh = login.json()["refresh_token"]

    old_rt_in_db = (
        db_test_session.execute(
            select(RefreshToken).where(
                RefreshToken.user_id == u.id, RefreshToken.revoked_at.is_(None)
            )
        )
        .scalars()
        .first()
    )
    assert old_rt_in_db is not None
    old_jti = old_rt_in_db.jti

    def throw_an_exception(*args, **kwargs):
        raise Exception("DB insert failed")

    monkeypatch.setattr(RefreshTokenRepository, "create", throw_an_exception())

    resp = test_client.post("/auth/refresh", params={"refresh_token": old_refresh})
    assert resp.status_code == 500

    old_rt_is_still_active = (
        db_test_session.execute(select(RefreshToken).where(RefreshToken.jti == old_jti))
        .scalars()
        .first()
    )
    assert old_rt_is_still_active is not None
    assert old_rt_is_still_active.revoked_at is None
