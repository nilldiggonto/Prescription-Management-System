from datetime import datetime, timedelta, timezone

from httpx import AsyncClient
from sqlalchemy import select

from app.models.access_token import AccessToken
from app.models.user import User
from tests.conftest import FakeEmailSender, register_and_verify_user

EMAIL = "me-user@example.com"
PASSWORD = "supersecret123"


async def _login(client: AsyncClient, fake_email_sender: FakeEmailSender) -> None:
    await register_and_verify_user(client, fake_email_sender, email=EMAIL, password=PASSWORD)
    response = await client.post("/api/v1/auth/login", json={"email": EMAIL, "password": PASSWORD})
    assert response.status_code == 200


async def test_me_with_valid_session_returns_user(client: AsyncClient, fake_email_sender: FakeEmailSender):
    await _login(client, fake_email_sender)

    response = await client.get("/api/v1/auth/me")

    assert response.status_code == 200
    assert response.json()["email"] == EMAIL


async def test_me_without_cookie_returns_401(client: AsyncClient):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


async def test_me_with_garbage_cookie_returns_401(client: AsyncClient):
    client.cookies.set("access_token", "not-a-real-token")
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


async def test_me_with_expired_token_returns_401(client: AsyncClient, db_session, fake_email_sender: FakeEmailSender):
    await _login(client, fake_email_sender)

    result = await db_session.execute(select(User).where(User.email == EMAIL))
    user = result.scalar_one()
    token_result = await db_session.execute(select(AccessToken).where(AccessToken.user_id == user.id))
    access_token = token_result.scalars().first()
    access_token.expires_at = datetime.now(timezone.utc) - timedelta(days=1)
    await db_session.commit()

    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


async def test_me_with_revoked_token_returns_401(client: AsyncClient, db_session, fake_email_sender: FakeEmailSender):
    await _login(client, fake_email_sender)

    result = await db_session.execute(select(User).where(User.email == EMAIL))
    user = result.scalar_one()
    token_result = await db_session.execute(select(AccessToken).where(AccessToken.user_id == user.id))
    access_token = token_result.scalars().first()
    access_token.revoked_at = datetime.now(timezone.utc)
    await db_session.commit()

    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401
