from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.user import User, UserRole
from tests.conftest import FakeEmailSender, register_and_verify_user

DOCTOR_EMAIL = "admin-target@example.com"
ADMIN_EMAIL = "the-admin@example.com"
PASSWORD = "supersecret123"


async def _login_doctor(client: AsyncClient, fake_email_sender: FakeEmailSender) -> str:
    await register_and_verify_user(client, fake_email_sender, email=DOCTOR_EMAIL, password=PASSWORD)
    response = await client.post("/api/v1/auth/login", json={"email": DOCTOR_EMAIL, "password": PASSWORD})
    assert response.status_code == 200
    return response.json()["id"]


async def _login_admin(client: AsyncClient, db_session: AsyncSession) -> None:
    admin = User(
        email=ADMIN_EMAIL, hashed_password=hash_password(PASSWORD), role=UserRole.ADMIN, is_verified=True
    )
    db_session.add(admin)
    await db_session.commit()

    response = await client.post("/api/v1/auth/login", json={"email": ADMIN_EMAIL, "password": PASSWORD})
    assert response.status_code == 200


async def test_admin_routes_require_admin_role(
    client: AsyncClient, fake_email_sender: FakeEmailSender, db_session: AsyncSession
):
    user_id = await _login_doctor(client, fake_email_sender)
    csrf_token = client.cookies.get("csrf_token")

    assert (await client.get("/api/v1/admin/users")).status_code == 403
    assert (
        await client.patch(
            f"/api/v1/admin/users/{user_id}/subscription",
            json={"plan": "pro"},
            headers={"X-CSRF-Token": csrf_token},
        )
    ).status_code == 403
    assert (
        await client.patch(
            f"/api/v1/admin/users/{user_id}/status",
            json={"is_active": False},
            headers={"X-CSRF-Token": csrf_token},
        )
    ).status_code == 403


async def test_admin_can_list_and_override_plan(
    client: AsyncClient, fake_email_sender: FakeEmailSender, db_session: AsyncSession
):
    user_id = await _login_doctor(client, fake_email_sender)

    client.cookies.clear()
    await _login_admin(client, db_session)
    csrf_token = client.cookies.get("csrf_token")

    list_response = await client.get("/api/v1/admin/users")
    assert list_response.status_code == 200
    emails = [row["email"] for row in list_response.json()]
    assert DOCTOR_EMAIL in emails

    override_response = await client.patch(
        f"/api/v1/admin/users/{user_id}/subscription",
        json={"plan": "premium"},
        headers={"X-CSRF-Token": csrf_token},
    )
    assert override_response.status_code == 200
    assert override_response.json()["plan"] == "premium"


async def test_admin_can_suspend_doctor_account(
    client: AsyncClient, fake_email_sender: FakeEmailSender, db_session: AsyncSession
):
    await _login_doctor(client, fake_email_sender)

    client.cookies.clear()
    await _login_admin(client, db_session)
    csrf_token = client.cookies.get("csrf_token")

    list_response = await client.get("/api/v1/admin/users")
    doctor_row = next(row for row in list_response.json() if row["email"] == DOCTOR_EMAIL)

    status_response = await client.patch(
        f"/api/v1/admin/users/{doctor_row['id']}/status",
        json={"is_active": False},
        headers={"X-CSRF-Token": csrf_token},
    )
    assert status_response.status_code == 200
    assert status_response.json()["is_active"] is False

    client.cookies.clear()
    login_response = await client.post("/api/v1/auth/login", json={"email": DOCTOR_EMAIL, "password": PASSWORD})
    assert login_response.status_code == 403
    assert "suspended" in login_response.json()["detail"].lower()
