from datetime import datetime, timedelta, timezone

from httpx import AsyncClient
from sqlalchemy import select

from app.core.config import get_settings
from app.models.otp import EmailVerificationOTP
from app.models.user import User
from tests.conftest import FakeEmailSender


async def _register(client: AsyncClient, email: str = "verify-me@example.com") -> None:
    response = await client.post("/api/v1/auth/register", json={"email": email, "password": "supersecret123"})
    assert response.status_code == 201


async def _get_otp_record(db_session, email: str) -> EmailVerificationOTP:
    user_result = await db_session.execute(select(User).where(User.email == email))
    user = user_result.scalar_one()
    otp_result = await db_session.execute(
        select(EmailVerificationOTP).where(EmailVerificationOTP.user_id == user.id)
    )
    return otp_result.scalar_one()


async def test_verify_email_with_valid_otp_succeeds(client: AsyncClient, db_session, fake_email_sender: FakeEmailSender):
    await _register(client)
    raw_otp = fake_email_sender.sent[0]["otp"]

    response = await client.post(
        "/api/v1/auth/verify-email", json={"email": "verify-me@example.com", "otp": raw_otp}
    )

    assert response.status_code == 200

    result = await db_session.execute(select(User).where(User.email == "verify-me@example.com"))
    user = result.scalar_one()
    assert user.is_verified is True

    otp_record = await _get_otp_record(db_session, "verify-me@example.com")
    assert otp_record.used_at is not None


async def test_verify_email_with_unknown_email_returns_400(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/verify-email", json={"email": "nobody@example.com", "otp": "123456"}
    )
    assert response.status_code == 400


async def test_verify_email_with_wrong_otp_returns_400_and_increments_attempts(
    client: AsyncClient, db_session, fake_email_sender: FakeEmailSender
):
    await _register(client)
    raw_otp = fake_email_sender.sent[0]["otp"]
    wrong_otp = "000000" if raw_otp != "000000" else "111111"

    response = await client.post(
        "/api/v1/auth/verify-email", json={"email": "verify-me@example.com", "otp": wrong_otp}
    )
    assert response.status_code == 400

    otp_record = await _get_otp_record(db_session, "verify-me@example.com")
    assert otp_record.attempt_count == 1


async def test_verify_email_with_already_used_otp_returns_400(client: AsyncClient, fake_email_sender: FakeEmailSender):
    await _register(client)
    raw_otp = fake_email_sender.sent[0]["otp"]
    payload = {"email": "verify-me@example.com", "otp": raw_otp}

    first = await client.post("/api/v1/auth/verify-email", json=payload)
    assert first.status_code == 200

    second = await client.post("/api/v1/auth/verify-email", json=payload)
    assert second.status_code == 400


async def test_verify_email_with_expired_otp_returns_400(client: AsyncClient, db_session, fake_email_sender: FakeEmailSender):
    await _register(client)
    raw_otp = fake_email_sender.sent[0]["otp"]

    otp_record = await _get_otp_record(db_session, "verify-me@example.com")
    otp_record.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    await db_session.commit()

    response = await client.post(
        "/api/v1/auth/verify-email", json={"email": "verify-me@example.com", "otp": raw_otp}
    )
    assert response.status_code == 400


async def test_verify_email_locks_out_after_max_attempts(
    client: AsyncClient, db_session, fake_email_sender: FakeEmailSender
):
    await _register(client)
    raw_otp = fake_email_sender.sent[0]["otp"]
    wrong_otp = "000000" if raw_otp != "000000" else "111111"
    max_attempts = get_settings().email_verification_otp_max_attempts

    for _ in range(max_attempts):
        response = await client.post(
            "/api/v1/auth/verify-email", json={"email": "verify-me@example.com", "otp": wrong_otp}
        )
        assert response.status_code == 400

    # Even the correct OTP is now rejected because the attempt budget is exhausted.
    response = await client.post(
        "/api/v1/auth/verify-email", json={"email": "verify-me@example.com", "otp": raw_otp}
    )
    assert response.status_code == 400


async def test_verify_email_with_malformed_otp_returns_422(client: AsyncClient, fake_email_sender: FakeEmailSender):
    await _register(client)
    response = await client.post(
        "/api/v1/auth/verify-email", json={"email": "verify-me@example.com", "otp": "12"}
    )
    assert response.status_code == 422