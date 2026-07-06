from httpx import AsyncClient
from sqlalchemy import select

from app.models.user import User
from tests.conftest import FakeEmailSender


async def test_register_success(client: AsyncClient, db_session, fake_email_sender: FakeEmailSender):
    response = await client.post(
        "/api/v1/auth/register", json={"email": "doctor@example.com", "password": "supersecret123"}
    )

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "doctor@example.com"
    assert body["is_verified"] is False
    assert "hashed_password" not in body

    result = await db_session.execute(select(User).where(User.email == "doctor@example.com"))
    user = result.scalar_one()
    assert user.is_verified is False
    assert user.hashed_password != "supersecret123"

    assert len(fake_email_sender.sent) == 1
    assert fake_email_sender.sent[0]["to"] == "doctor@example.com"


async def test_register_duplicate_email_returns_409(client: AsyncClient):
    payload = {"email": "dup@example.com", "password": "supersecret123"}

    first = await client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 201

    second = await client.post("/api/v1/auth/register", json=payload)
    assert second.status_code == 409


async def test_register_invalid_email_returns_422(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/register", json={"email": "not-an-email", "password": "supersecret123"}
    )
    assert response.status_code == 422


async def test_register_short_password_returns_422(client: AsyncClient):
    response = await client.post("/api/v1/auth/register", json={"email": "shortpw@example.com", "password": "abc"})
    assert response.status_code == 422


async def test_register_password_without_digit_returns_422(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/register", json={"email": "noletters@example.com", "password": "allletters"}
    )
    assert response.status_code == 422


async def test_register_password_without_letter_returns_422(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/register", json={"email": "nodigits@example.com", "password": "12345678"}
    )
    assert response.status_code == 422
