from httpx import AsyncClient

from tests.conftest import FakeEmailSender, register_and_verify_user

EMAIL = "logout-me@example.com"
PASSWORD = "supersecret123"


async def _login(client: AsyncClient, fake_email_sender: FakeEmailSender) -> None:
    await register_and_verify_user(client, fake_email_sender, email=EMAIL, password=PASSWORD)
    response = await client.post("/api/v1/auth/login", json={"email": EMAIL, "password": PASSWORD})
    assert response.status_code == 200


async def test_logout_without_csrf_header_returns_403(client: AsyncClient, fake_email_sender: FakeEmailSender):
    await _login(client, fake_email_sender)

    response = await client.post("/api/v1/auth/logout")
    assert response.status_code == 403


async def test_logout_with_mismatched_csrf_header_returns_403(client: AsyncClient, fake_email_sender: FakeEmailSender):
    await _login(client, fake_email_sender)

    response = await client.post("/api/v1/auth/logout", headers={"X-CSRF-Token": "wrong-value"})
    assert response.status_code == 403


async def test_logout_revokes_session_and_clears_cookies(client: AsyncClient, fake_email_sender: FakeEmailSender):
    await _login(client, fake_email_sender)
    csrf_token = client.cookies.get("csrf_token")

    response = await client.post("/api/v1/auth/logout", headers={"X-CSRF-Token": csrf_token})
    assert response.status_code == 200

    me_response = await client.get("/api/v1/auth/me")
    assert me_response.status_code == 401


async def test_logout_is_idempotent(client: AsyncClient, fake_email_sender: FakeEmailSender):
    await _login(client, fake_email_sender)
    csrf_token = client.cookies.get("csrf_token")
    access_token = client.cookies.get("access_token")

    first = await client.post("/api/v1/auth/logout", headers={"X-CSRF-Token": csrf_token})
    assert first.status_code == 200

    # Logout clears cookies client-side, so re-attach the now-stale ones to prove the
    # underlying revoke on an already-revoked token doesn't error (service-level idempotency),
    # independent of the fact a real client would no longer have them to send.
    client.cookies.set("access_token", access_token)
    client.cookies.set("csrf_token", csrf_token)

    second = await client.post("/api/v1/auth/logout", headers={"X-CSRF-Token": csrf_token})
    assert second.status_code == 200
