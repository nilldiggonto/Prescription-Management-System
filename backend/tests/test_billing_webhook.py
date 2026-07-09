import hashlib
import hmac
import json
import time

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.subscription import Subscription, SubscriptionPlan, SubscriptionStatus
from app.services.subscription_service import SubscriptionService
from tests.conftest import FakeEmailSender, register_and_verify_user

EMAIL = "webhook-doctor@example.com"
PASSWORD = "supersecret123"


async def _register(client: AsyncClient, fake_email_sender: FakeEmailSender) -> str:
    await register_and_verify_user(client, fake_email_sender, email=EMAIL, password=PASSWORD)
    me_response = await client.post("/api/v1/auth/login", json={"email": EMAIL, "password": PASSWORD})
    assert me_response.status_code == 200
    return me_response.json()["id"]


async def test_checkout_completed_upgrades_plan(
    client: AsyncClient, fake_email_sender: FakeEmailSender, db_session: AsyncSession
):
    user_id = await _register(client, fake_email_sender)

    event = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "customer": "cus_test123",
                "subscription": "sub_test123",
                "metadata": {"user_id": user_id, "plan": "pro"},
            }
        },
    }
    await SubscriptionService(db_session, get_settings()).handle_webhook_event(event)

    result = await db_session.execute(select(Subscription).where(Subscription.user_id == user_id))
    subscription = result.scalar_one()
    assert subscription.plan == SubscriptionPlan.PRO
    assert subscription.status == SubscriptionStatus.ACTIVE
    assert subscription.stripe_customer_id == "cus_test123"
    assert subscription.stripe_subscription_id == "sub_test123"


async def test_subscription_deleted_reverts_to_free(
    client: AsyncClient, fake_email_sender: FakeEmailSender, db_session: AsyncSession
):
    user_id = await _register(client, fake_email_sender)
    service = SubscriptionService(db_session, get_settings())

    await service.handle_webhook_event(
        {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "customer": "cus_test456",
                    "subscription": "sub_test456",
                    "metadata": {"user_id": user_id, "plan": "premium"},
                }
            },
        }
    )

    await service.handle_webhook_event(
        {"type": "customer.subscription.deleted", "data": {"object": {"id": "sub_test456", "status": "canceled"}}}
    )

    result = await db_session.execute(select(Subscription).where(Subscription.user_id == user_id))
    subscription = result.scalar_one()
    assert subscription.plan == SubscriptionPlan.FREE
    assert subscription.status == SubscriptionStatus.CANCELED


def _sign(payload: bytes, secret: str) -> str:
    timestamp = str(int(time.time()))
    signed_payload = f"{timestamp}.{payload.decode()}".encode()
    signature = hmac.new(secret.encode(), signed_payload, hashlib.sha256).hexdigest()
    return f"t={timestamp},v1={signature}"


async def test_webhook_endpoint_rejects_invalid_signature(client: AsyncClient):
    payload = json.dumps({"type": "checkout.session.completed", "data": {"object": {}}}).encode()
    response = await client.post(
        "/api/v1/billing/webhook",
        content=payload,
        headers={"stripe-signature": "t=1,v1=deadbeef", "content-type": "application/json"},
    )
    assert response.status_code == 400


async def test_webhook_endpoint_accepts_valid_signature(client: AsyncClient):
    settings = get_settings()
    payload = json.dumps(
        {
            "id": "evt_test123",
            "object": "event",
            "type": "customer.subscription.updated",
            "data": {"object": {"id": "sub_nonexistent", "status": "active"}},
        }
    ).encode()
    signature = _sign(payload, settings.stripe_webhook_secret)

    response = await client.post(
        "/api/v1/billing/webhook",
        content=payload,
        headers={"stripe-signature": signature, "content-type": "application/json"},
    )
    assert response.status_code == 200
