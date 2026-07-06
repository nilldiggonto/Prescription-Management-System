from datetime import datetime, timedelta, timezone

from httpx import AsyncClient
from sqlalchemy import select

from app.core.config import get_settings
from app.models.access_token import AccessToken
from app.models.password_reset_otp import PasswordResetOTP
from app.models.user import User
from tests.conftest import FakeEmailSender, register_and_verify_user

EMAIL = "reset-me@example.com"
PASSWORD = "supersecret123"
NEW_PASSWORD = "evennewerpass1"


async def _get_reset_otp_record(db_session, email: str) -> PasswordResetOTP:
    user_result = await db_session.execute(select(User).where(User.email == email))
    user = user_result.scalar_one()
    otp_result = await db_session.execute(select(PasswordResetOTP).where(PasswordResetOTP.user_id == user.id))
    return otp_result.scalars().first()


async def test_forgot_password_returns_200_for_existing_email(
    client: AsyncClient, fake_email_sender: FakeEmailSender
):
    await register_and_verify_user(client, fake_email_sender, email=EMAIL, password=PASSWORD)

    response = await client.post("/api/v1/auth/forgot-password", json={"email": EMAIL})

    assert response.status_code == 200
    assert len(fake_email_sender.password_reset_sent) == 1
    assert fake_email_sender.password_reset_sent[0]["to"] == EMAIL


async def test_forgot_password_returns_200_for_unknown_email(client: AsyncClient, fake_email_sender: FakeEmailSender):
    response = await client.post("/api/v1/auth/forgot-password", json={"email": "nobody@example.com"})

    assert response.status_code == 200
    assert len(fake_email_sender.password_reset_sent) == 0


async def test_reset_password_success_changes_password_and_revokes_sessions(
    client: AsyncClient, db_session, fake_email_sender: FakeEmailSender
):
    await register_and_verify_user(client, fake_email_sender, email=EMAIL, password=PASSWORD)
    login_response = await client.post("/api/v1/auth/login", json={"email": EMAIL, "password": PASSWORD})
    assert login_response.status_code == 200

    forgot_response = await client.post("/api/v1/auth/forgot-password", json={"email": EMAIL})
    assert forgot_response.status_code == 200
    raw_otp = fake_email_sender.password_reset_sent[0]["otp"]

    reset_response = await client.post(
        "/api/v1/auth/reset-password", json={"email": EMAIL, "otp": raw_otp, "new_password": NEW_PASSWORD}
    )
    assert reset_response.status_code == 200

    old_password_login = await client.post("/api/v1/auth/login", json={"email": EMAIL, "password": PASSWORD})
    assert old_password_login.status_code == 401

    new_password_login = await client.post("/api/v1/auth/login", json={"email": EMAIL, "password": NEW_PASSWORD})
    assert new_password_login.status_code == 200

    user_result = await db_session.execute(select(User).where(User.email == EMAIL))
    user = user_result.scalar_one()
    tokens_result = await db_session.execute(
        select(AccessToken).where(AccessToken.user_id == user.id, AccessToken.revoked_at.is_(None))
    )
    active_tokens = tokens_result.scalars().all()
    # Only the token from the post-reset login above should still be active; the
    # pre-reset session must have been revoked.
    assert len(active_tokens) == 1


async def test_reset_password_wrong_otp_increments_attempts(
    client: AsyncClient, db_session, fake_email_sender: FakeEmailSender
):
    await register_and_verify_user(client, fake_email_sender, email=EMAIL, password=PASSWORD)
    await client.post("/api/v1/auth/forgot-password", json={"email": EMAIL})
    raw_otp = fake_email_sender.password_reset_sent[0]["otp"]
    wrong_otp = "000000" if raw_otp != "000000" else "111111"

    response = await client.post(
        "/api/v1/auth/reset-password", json={"email": EMAIL, "otp": wrong_otp, "new_password": NEW_PASSWORD}
    )
    assert response.status_code == 400

    otp_record = await _get_reset_otp_record(db_session, EMAIL)
    assert otp_record.attempt_count == 1


async def test_reset_password_expired_otp_returns_400(
    client: AsyncClient, db_session, fake_email_sender: FakeEmailSender
):
    await register_and_verify_user(client, fake_email_sender, email=EMAIL, password=PASSWORD)
    await client.post("/api/v1/auth/forgot-password", json={"email": EMAIL})
    raw_otp = fake_email_sender.password_reset_sent[0]["otp"]

    otp_record = await _get_reset_otp_record(db_session, EMAIL)
    otp_record.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    await db_session.commit()

    response = await client.post(
        "/api/v1/auth/reset-password", json={"email": EMAIL, "otp": raw_otp, "new_password": NEW_PASSWORD}
    )
    assert response.status_code == 400


async def test_reset_password_locks_out_after_max_attempts(
    client: AsyncClient, fake_email_sender: FakeEmailSender
):
    await register_and_verify_user(client, fake_email_sender, email=EMAIL, password=PASSWORD)
    await client.post("/api/v1/auth/forgot-password", json={"email": EMAIL})
    raw_otp = fake_email_sender.password_reset_sent[0]["otp"]
    wrong_otp = "000000" if raw_otp != "000000" else "111111"
    max_attempts = get_settings().password_reset_otp_max_attempts

    for _ in range(max_attempts):
        response = await client.post(
            "/api/v1/auth/reset-password", json={"email": EMAIL, "otp": wrong_otp, "new_password": NEW_PASSWORD}
        )
        assert response.status_code == 400

    response = await client.post(
        "/api/v1/auth/reset-password", json={"email": EMAIL, "otp": raw_otp, "new_password": NEW_PASSWORD}
    )
    assert response.status_code == 400
