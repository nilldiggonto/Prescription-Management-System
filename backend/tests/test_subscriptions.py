import stripe
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subscription import Subscription, SubscriptionPlan
from tests.conftest import FakeEmailSender, register_and_verify_user

EMAIL = "subscriber@example.com"
PASSWORD = "supersecret123"

DOCTOR_PROFILE_PAYLOAD = {
    "full_name": "Dr. Jane Doe",
    "degrees": "MBBS",
    "specialization": None,
    "registration_number": "A-99999",
    "hospital_name": None,
    "chamber_address": None,
    "phone": None,
    "signature_url": None,
    "logo_url": None,
}

NEW_PATIENT_PAYLOAD = {
    "full_name": "John Patient",
    "age": 34,
    "gender": "male",
    "phone": "+8801711111111",
    "address": None,
}

MEDICINES_PAYLOAD = [
    {"name": "Paracetamol", "dosage": "500mg", "frequency": "1+1+1", "duration": "5 days", "instructions": None},
]


async def _login_with_profile(client: AsyncClient, fake_email_sender: FakeEmailSender, email: str = EMAIL) -> str:
    await register_and_verify_user(client, fake_email_sender, email=email, password=PASSWORD)
    login_response = await client.post("/api/v1/auth/login", json={"email": email, "password": PASSWORD})
    assert login_response.status_code == 200

    csrf_token = client.cookies.get("csrf_token")
    profile_response = await client.put(
        "/api/v1/doctor-profile/me", json=DOCTOR_PROFILE_PAYLOAD, headers={"X-CSRF-Token": csrf_token}
    )
    assert profile_response.status_code == 200
    return csrf_token


async def _create_prescription(client: AsyncClient, csrf_token: str) -> int:
    response = await client.post(
        "/api/v1/prescriptions",
        json={"new_patient": NEW_PATIENT_PAYLOAD, "medicines": MEDICINES_PAYLOAD},
        headers={"X-CSRF-Token": csrf_token},
    )
    return response.status_code


async def test_subscription_created_as_free_on_registration(client: AsyncClient, fake_email_sender: FakeEmailSender):
    await _login_with_profile(client, fake_email_sender)

    response = await client.get("/api/v1/billing/me")
    assert response.status_code == 200
    body = response.json()
    assert body["plan"] == "free"
    assert body["daily_limit"] == 20
    assert body["used_today"] == 0


async def test_billing_me_reflects_usage(client: AsyncClient, fake_email_sender: FakeEmailSender):
    csrf_token = await _login_with_profile(client, fake_email_sender)

    for _ in range(3):
        assert await _create_prescription(client, csrf_token) == 201

    response = await client.get("/api/v1/billing/me")
    assert response.json()["used_today"] == 3


async def test_free_plan_blocked_after_daily_limit(client: AsyncClient, fake_email_sender: FakeEmailSender):
    csrf_token = await _login_with_profile(client, fake_email_sender)

    for _ in range(20):
        assert await _create_prescription(client, csrf_token) == 201

    response = await client.post(
        "/api/v1/prescriptions",
        json={"new_patient": NEW_PATIENT_PAYLOAD, "medicines": MEDICINES_PAYLOAD},
        headers={"X-CSRF-Token": csrf_token},
    )
    assert response.status_code == 429


async def test_premium_plan_is_never_blocked(
    client: AsyncClient, fake_email_sender: FakeEmailSender, db_session: AsyncSession
):
    csrf_token = await _login_with_profile(client, fake_email_sender)

    # Bypass the API and directly promote this doctor to Premium — the admin-override
    # endpoint itself is covered separately in test_admin.py; this test only cares that
    # a Premium subscription is exempt from the daily-limit check.
    me_response = await client.get("/api/v1/auth/me")
    user_id = me_response.json()["id"]
    result = await db_session.execute(select(Subscription).where(Subscription.user_id == user_id))
    subscription = result.scalar_one()
    subscription.plan = SubscriptionPlan.PREMIUM
    await db_session.commit()

    for _ in range(25):
        assert await _create_prescription(client, csrf_token) == 201


class _FakeCheckoutSession:
    def __init__(self, client_reference_id: str, data: dict):
        self.client_reference_id = client_reference_id
        self._data = data

    def to_dict(self) -> dict:
        return self._data


async def test_sync_checkout_updates_plan_after_stripe_redirect(
    client: AsyncClient, fake_email_sender: FakeEmailSender, monkeypatch
):
    csrf_token = await _login_with_profile(client, fake_email_sender)
    me_response = await client.get("/api/v1/auth/me")
    user_id = me_response.json()["id"]

    fake_session = _FakeCheckoutSession(
        client_reference_id=user_id,
        data={"customer": "cus_sync1", "subscription": "sub_sync1", "metadata": {"user_id": user_id, "plan": "pro"}},
    )

    async def fake_retrieve_async(self, session, params=None, options=None):
        return fake_session

    monkeypatch.setattr(stripe.checkout.SessionService, "retrieve_async", fake_retrieve_async)

    response = await client.post(
        "/api/v1/billing/sync-checkout",
        json={"session_id": "cs_test_abc"},
        headers={"X-CSRF-Token": csrf_token},
    )
    assert response.status_code == 200
    assert response.json()["plan"] == "pro"


async def test_sync_checkout_rejects_session_belonging_to_another_user(
    client: AsyncClient, fake_email_sender: FakeEmailSender, monkeypatch
):
    csrf_token = await _login_with_profile(client, fake_email_sender)

    fake_session = _FakeCheckoutSession(
        client_reference_id="00000000-0000-0000-0000-000000000000",
        data={"customer": "cus_x", "subscription": "sub_x", "metadata": {}},
    )

    async def fake_retrieve_async(self, session, params=None, options=None):
        return fake_session

    monkeypatch.setattr(stripe.checkout.SessionService, "retrieve_async", fake_retrieve_async)

    response = await client.post(
        "/api/v1/billing/sync-checkout",
        json={"session_id": "cs_test_other"},
        headers={"X-CSRF-Token": csrf_token},
    )
    assert response.status_code == 403
