import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.api.deps import AppSettings, CurrentUser, DbSession, verify_csrf_token
from app.schemas.subscription import (
    CheckoutRequest,
    CheckoutResponse,
    PortalResponse,
    SubscriptionRead,
    SyncCheckoutRequest,
)
from app.services.subscription_service import SubscriptionService

router = APIRouter(prefix="/billing", tags=["billing"])


@router.get("/me", response_model=SubscriptionRead)
async def get_my_subscription(current_user: CurrentUser, session: DbSession, settings: AppSettings) -> SubscriptionRead:
    return await SubscriptionService(session, settings).get_billing_info(current_user)


@router.post("/sync-checkout", response_model=SubscriptionRead, dependencies=[Depends(verify_csrf_token)])
async def sync_checkout_session(
    payload: SyncCheckoutRequest, current_user: CurrentUser, session: DbSession, settings: AppSettings
) -> SubscriptionRead:
    return await SubscriptionService(session, settings).sync_from_checkout_session(current_user, payload.session_id)


@router.post("/checkout", response_model=CheckoutResponse, dependencies=[Depends(verify_csrf_token)])
async def create_checkout_session(
    payload: CheckoutRequest, current_user: CurrentUser, session: DbSession, settings: AppSettings
) -> CheckoutResponse:
    checkout_url = await SubscriptionService(session, settings).create_checkout_session(current_user, payload.plan)
    return CheckoutResponse(checkout_url=checkout_url)


@router.post("/portal", response_model=PortalResponse, dependencies=[Depends(verify_csrf_token)])
async def create_portal_session(current_user: CurrentUser, session: DbSession, settings: AppSettings) -> PortalResponse:
    portal_url = await SubscriptionService(session, settings).create_portal_session(current_user)
    return PortalResponse(portal_url=portal_url)


@router.post("/webhook", include_in_schema=False)
async def stripe_webhook(request: Request, session: DbSession, settings: AppSettings) -> dict:
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    if sig_header is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing Stripe-Signature header")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.stripe_webhook_secret)
    except (ValueError, stripe.SignatureVerificationError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid webhook payload") from exc

    await SubscriptionService(session, settings).handle_webhook_event(event)
    return {"received": True}
