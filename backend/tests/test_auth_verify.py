from datetime import datetime, timedelta, timezone

from httpx import AsyncClient
from sqlalchemy import select

from app.core.security import hash_token
from app.models.tokens import EmailVerificationToken
from app.models.user import User
from tests.conftest import FakeEmailSender


async def _register(client: AsyncClient, email: str = "verify-me@example.com") -> None:
    response = await client.post("/api/v1/auth/register", json={"email": email, "password": "supersecret123"})
    assert response.status_code == 201


async def test_verify_email_with_valid_token_succeeds(
    client: AsyncClient, db_session, fake_email_sender: FakeEmailSender
):
    await _register(client)
    raw_token = fake_email_sender.sent[0]["token"]

    response = await client.get("/api/v1/auth/verify-email", params={"token": raw_token})

    assert response.status_code == 200

    result = await db_session.execute(select(User).where(User.email == "verify-me@example.com"))
    user = result.scalar_one()
    assert user.is_verified is True

    token_result = await db_session.execute(
        select(EmailVerificationToken).where(EmailVerificationToken.token_hash == hash_token(raw_token))
    )
    token = token_result.scalar_one()
    assert token.used_at is not None


async def test_verify_email_with_unknown_token_returns_400(client: AsyncClient):
    response = await client.get("/api/v1/auth/verify-email", params={"token": "not-a-real-token"})
    assert response.status_code == 400


async def test_verify_email_with_already_used_token_returns_400(client: AsyncClient, fake_email_sender: FakeEmailSender):
    await _register(client)
    raw_token = fake_email_sender.sent[0]["token"]

    first = await client.get("/api/v1/auth/verify-email", params={"token": raw_token})
    assert first.status_code == 200

    second = await client.get("/api/v1/auth/verify-email", params={"token": raw_token})
    assert second.status_code == 400


async def test_verify_email_with_expired_token_returns_400(client: AsyncClient, db_session, fake_email_sender: FakeEmailSender):
    await _register(client)
    raw_token = fake_email_sender.sent[0]["token"]

    result = await db_session.execute(
        select(EmailVerificationToken).where(EmailVerificationToken.token_hash == hash_token(raw_token))
    )
    token = result.scalar_one()
    token.expires_at = datetime.now(timezone.utc) - timedelta(hours=1)
    await db_session.commit()

    response = await client.get("/api/v1/auth/verify-email", params={"token": raw_token})
    assert response.status_code == 400
