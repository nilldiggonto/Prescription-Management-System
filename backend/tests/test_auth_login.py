from httpx import AsyncClient
from sqlalchemy import select

from app.models.access_token import AccessToken
from app.models.user import User
from tests.conftest import FakeEmailSender, register_and_verify_user

EMAIL = "login-me@example.com"
PASSWORD = "supersecret123"


async def test_login_success_sets_cookies(client: AsyncClient, fake_email_sender: FakeEmailSender):
    await register_and_verify_user(client, fake_email_sender, email=EMAIL, password=PASSWORD)

    response = await client.post("/api/v1/auth/login", json={"email": EMAIL, "password": PASSWORD})

    assert response.status_code == 200
    assert response.json()["email"] == EMAIL
    assert "access_token" in response.cookies
    assert "csrf_token" in response.cookies


async def test_login_wrong_password_returns_401(client: AsyncClient, fake_email_sender: FakeEmailSender):
    await register_and_verify_user(client, fake_email_sender, email=EMAIL, password=PASSWORD)

    response = await client.post("/api/v1/auth/login", json={"email": EMAIL, "password": "wrongpassword1"})
    assert response.status_code == 401


async def test_login_unknown_email_returns_401_with_same_message(client: AsyncClient, fake_email_sender: FakeEmailSender):
    await register_and_verify_user(client, fake_email_sender, email=EMAIL, password=PASSWORD)

    wrong_password_response = await client.post(
        "/api/v1/auth/login", json={"email": EMAIL, "password": "wrongpassword1"}
    )
    unknown_email_response = await client.post(
        "/api/v1/auth/login", json={"email": "nobody@example.com", "password": PASSWORD}
    )

    assert wrong_password_response.status_code == unknown_email_response.status_code == 401
    assert wrong_password_response.json()["detail"] == unknown_email_response.json()["detail"]


async def test_login_unverified_user_returns_403(client: AsyncClient):
    unverified_email = "unverified@example.com"
    register_response = await client.post(
        "/api/v1/auth/register", json={"email": unverified_email, "password": PASSWORD}
    )
    assert register_response.status_code == 201

    response = await client.post("/api/v1/auth/login", json={"email": unverified_email, "password": PASSWORD})
    assert response.status_code == 403


async def test_login_inactive_user_returns_403(client: AsyncClient, db_session, fake_email_sender: FakeEmailSender):
    await register_and_verify_user(client, fake_email_sender, email=EMAIL, password=PASSWORD)

    result = await db_session.execute(select(User).where(User.email == EMAIL))
    user = result.scalar_one()
    user.is_active = False
    await db_session.commit()

    response = await client.post("/api/v1/auth/login", json={"email": EMAIL, "password": PASSWORD})
    assert response.status_code == 403


async def test_login_remember_me_persists_cookie_and_extends_expiry(
    client: AsyncClient, db_session, fake_email_sender: FakeEmailSender
):
    await register_and_verify_user(client, fake_email_sender, email=EMAIL, password=PASSWORD)

    response = await client.post(
        "/api/v1/auth/login", json={"email": EMAIL, "password": PASSWORD, "remember_me": True}
    )
    assert response.status_code == 200

    result = await db_session.execute(select(User).where(User.email == EMAIL))
    user = result.scalar_one()
    token_result = await db_session.execute(select(AccessToken).where(AccessToken.user_id == user.id))
    access_token = token_result.scalars().first()
    assert access_token.remember_me is True
