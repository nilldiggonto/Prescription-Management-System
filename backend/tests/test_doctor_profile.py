from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.user import User, UserRole
from tests.conftest import FakeEmailSender, register_and_verify_user

EMAIL = "doctor@example.com"
PASSWORD = "supersecret123"

PROFILE_PAYLOAD = {
    "full_name": "Dr. Jane Doe",
    "degrees": "MBBS, FCPS (Medicine)",
    "specialization": "Cardiologist",
    "registration_number": "A-12345",
    "hospital_name": "City General Hospital",
    "chamber_address": "House 1, Road 2, Dhaka",
    "phone": "+8801700000000",
    "signature_url": None,
    "logo_url": None,
}


async def _login_doctor(client: AsyncClient, fake_email_sender: FakeEmailSender) -> None:
    await register_and_verify_user(client, fake_email_sender, email=EMAIL, password=PASSWORD)
    response = await client.post("/api/v1/auth/login", json={"email": EMAIL, "password": PASSWORD})
    assert response.status_code == 200


async def _login_admin(client: AsyncClient, db_session: AsyncSession) -> None:
    admin = User(
        email="admin@example.com",
        hashed_password=hash_password(PASSWORD),
        role=UserRole.ADMIN,
        is_verified=True,
    )
    db_session.add(admin)
    await db_session.commit()

    response = await client.post("/api/v1/auth/login", json={"email": admin.email, "password": PASSWORD})
    assert response.status_code == 200


async def test_get_profile_requires_auth(client: AsyncClient):
    response = await client.get("/api/v1/doctor-profile/me")
    assert response.status_code == 401


async def test_get_profile_returns_404_when_not_set_up(client: AsyncClient, fake_email_sender: FakeEmailSender):
    await _login_doctor(client, fake_email_sender)

    response = await client.get("/api/v1/doctor-profile/me")
    assert response.status_code == 404


async def test_put_creates_profile(client: AsyncClient, fake_email_sender: FakeEmailSender):
    await _login_doctor(client, fake_email_sender)
    csrf_token = client.cookies.get("csrf_token")

    response = await client.put(
        "/api/v1/doctor-profile/me", json=PROFILE_PAYLOAD, headers={"X-CSRF-Token": csrf_token}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["full_name"] == PROFILE_PAYLOAD["full_name"]
    assert body["registration_number"] == PROFILE_PAYLOAD["registration_number"]

    get_response = await client.get("/api/v1/doctor-profile/me")
    assert get_response.status_code == 200
    assert get_response.json()["full_name"] == PROFILE_PAYLOAD["full_name"]


async def test_put_updates_existing_profile(client: AsyncClient, fake_email_sender: FakeEmailSender):
    await _login_doctor(client, fake_email_sender)
    csrf_token = client.cookies.get("csrf_token")

    first = await client.put("/api/v1/doctor-profile/me", json=PROFILE_PAYLOAD, headers={"X-CSRF-Token": csrf_token})
    assert first.status_code == 200
    first_id = first.json()["id"]

    updated_payload = {**PROFILE_PAYLOAD, "full_name": "Dr. Jane A. Doe", "hospital_name": "New Hospital"}
    second = await client.put(
        "/api/v1/doctor-profile/me", json=updated_payload, headers={"X-CSRF-Token": csrf_token}
    )
    assert second.status_code == 200
    body = second.json()
    assert body["id"] == first_id
    assert body["full_name"] == "Dr. Jane A. Doe"
    assert body["hospital_name"] == "New Hospital"


async def test_put_without_csrf_header_returns_403(client: AsyncClient, fake_email_sender: FakeEmailSender):
    await _login_doctor(client, fake_email_sender)

    response = await client.put("/api/v1/doctor-profile/me", json=PROFILE_PAYLOAD)
    assert response.status_code == 403


async def test_put_missing_required_field_returns_422(client: AsyncClient, fake_email_sender: FakeEmailSender):
    await _login_doctor(client, fake_email_sender)
    csrf_token = client.cookies.get("csrf_token")

    payload = {**PROFILE_PAYLOAD}
    del payload["registration_number"]

    response = await client.put("/api/v1/doctor-profile/me", json=payload, headers={"X-CSRF-Token": csrf_token})
    assert response.status_code == 422


async def test_admin_cannot_access_doctor_profile(client: AsyncClient, db_session: AsyncSession):
    await _login_admin(client, db_session)
    csrf_token = client.cookies.get("csrf_token")

    get_response = await client.get("/api/v1/doctor-profile/me")
    assert get_response.status_code == 403

    put_response = await client.put(
        "/api/v1/doctor-profile/me", json=PROFILE_PAYLOAD, headers={"X-CSRF-Token": csrf_token}
    )
    assert put_response.status_code == 403
