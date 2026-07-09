import uuid
from datetime import datetime, timezone

import stripe
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.plans import PLAN_DAILY_LIMITS
from app.models.subscription import Subscription, SubscriptionPlan, SubscriptionStatus
from app.models.user import User, UserRole
from app.repositories.prescription_repository import PrescriptionRepository
from app.repositories.subscription_repository import SubscriptionRepository
from app.repositories.user_repository import UserRepository
from app.schemas.admin import AdminUserRead
from app.schemas.subscription import SubscriptionRead


class SubscriptionService:
    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self._session = session
        self._settings = settings
        self._subscriptions = SubscriptionRepository(session)
        self._prescriptions = PrescriptionRepository(session)
        self._users = UserRepository(session)
        self._stripe = stripe.StripeClient(api_key=settings.stripe_secret_key)

    async def get_or_create_for_user(self, user: User) -> Subscription:
        subscription = await self._subscriptions.get_by_user_id(user.id)
        if subscription is None:
            # Defensive fallback — every doctor gets one at registration (AuthService.register),
            # this only matters for rows created before that existed.
            subscription = await self._subscriptions.create(user_id=user.id)
            await self._session.commit()
        return subscription

    async def get_billing_info(self, user: User) -> SubscriptionRead:
        _require_doctor(user)
        subscription = await self.get_or_create_for_user(user)
        used_today = await self._prescriptions.count_since_for_doctor(user.id, _start_of_today_utc())
        return SubscriptionRead(
            plan=subscription.plan,
            status=subscription.status,
            daily_limit=PLAN_DAILY_LIMITS[subscription.plan],
            used_today=used_today,
            current_period_end=subscription.current_period_end,
        )

    async def check_can_create_prescription(self, user: User) -> None:
        subscription = await self.get_or_create_for_user(user)
        limit = PLAN_DAILY_LIMITS[subscription.plan]
        if limit is None:
            return

        used_today = await self._prescriptions.count_since_for_doctor(user.id, _start_of_today_utc())
        if used_today >= limit:
            # subscription.plan is a str-backed enum column — see the comment on the
            # equivalent gender line in pdf_service.py. `.capitalize()`, not `.value`.
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=(
                    f"Daily limit reached for your {subscription.plan.capitalize()} plan "
                    f"({limit}/day). Upgrade for a higher limit."
                ),
            )

    async def create_checkout_session(self, user: User, plan: SubscriptionPlan) -> str:
        _require_doctor(user)
        subscription = await self.get_or_create_for_user(user)

        if subscription.stripe_customer_id is None:
            customer = await self._stripe.v1.customers.create_async(
                params={"email": user.email, "metadata": {"user_id": str(user.id)}}
            )
            subscription.stripe_customer_id = customer.id
            await self._session.commit()

        price_id = (
            self._settings.stripe_price_id_pro
            if plan == SubscriptionPlan.PRO
            else self._settings.stripe_price_id_premium
        )
        checkout_session = await self._stripe.v1.checkout.sessions.create_async(
            params={
                "mode": "subscription",
                "customer": subscription.stripe_customer_id,
                "line_items": [{"price": price_id, "quantity": 1}],
                "success_url": f"{self._settings.frontend_url}/dashboard/billing?checkout=success",
                "cancel_url": f"{self._settings.frontend_url}/dashboard/billing?checkout=cancel",
                "client_reference_id": str(user.id),
                "metadata": {"user_id": str(user.id), "plan": plan.value},
            }
        )
        return checkout_session.url

    async def create_portal_session(self, user: User) -> str:
        _require_doctor(user)
        subscription = await self.get_or_create_for_user(user)
        if subscription.stripe_customer_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="No billing history yet — upgrade a plan first"
            )

        portal_session = await self._stripe.v1.billing_portal.sessions.create_async(
            params={
                "customer": subscription.stripe_customer_id,
                "return_url": f"{self._settings.frontend_url}/dashboard/billing",
            }
        )
        return portal_session.url

    async def handle_webhook_event(self, event: dict) -> None:
        event_type = event["type"]
        data = event["data"]["object"]
        # The real Stripe SDK hands us a `StripeObject`, not a plain dict — it supports
        # `[...]` subscripting but not `.get(...)` (that falls through its __getattr__ and
        # raises). Normalize to a plain dict so the `.get()` calls below work regardless of
        # whether this came from a live webhook or a test fixture dict.
        if hasattr(data, "to_dict"):
            data = data.to_dict()

        if event_type == "checkout.session.completed":
            metadata = data.get("metadata") or {}
            user_id = metadata.get("user_id")
            plan_value = metadata.get("plan")
            if not user_id or not plan_value:
                return

            subscription = await self._subscriptions.get_by_user_id(uuid.UUID(user_id))
            if subscription is None:
                return

            subscription.stripe_customer_id = data["customer"]
            subscription.stripe_subscription_id = data["subscription"]
            subscription.plan = SubscriptionPlan(plan_value)
            subscription.status = SubscriptionStatus.ACTIVE
            await self._session.commit()

        elif event_type == "customer.subscription.updated":
            subscription = await self._subscriptions.get_by_stripe_subscription_id(data["id"])
            if subscription is None:
                return

            subscription.status = _map_stripe_status(data["status"])
            period_end = data.get("current_period_end")
            if period_end:
                subscription.current_period_end = datetime.fromtimestamp(period_end, tz=timezone.utc)
            await self._session.commit()

        elif event_type == "customer.subscription.deleted":
            subscription = await self._subscriptions.get_by_stripe_subscription_id(data["id"])
            if subscription is None:
                return

            subscription.plan = SubscriptionPlan.FREE
            subscription.status = SubscriptionStatus.CANCELED
            await self._session.commit()

    # --- Admin ---

    async def list_all_with_usage(self) -> list[AdminUserRead]:
        doctors = await self._users.list_by_role(UserRole.DOCTOR)
        usage_by_doctor = await self._prescriptions.count_since_grouped_by_doctor(_start_of_today_utc())
        subscriptions_by_user = await self._subscriptions.get_by_user_ids([doctor.id for doctor in doctors])

        rows: list[AdminUserRead] = []
        for doctor in doctors:
            subscription = subscriptions_by_user.get(doctor.id)
            if subscription is None:
                # Defensive fallback for doctors created before this feature existed.
                subscription = await self._subscriptions.create(user_id=doctor.id)
                await self._session.commit()

            rows.append(
                AdminUserRead(
                    id=doctor.id,
                    email=doctor.email,
                    role=doctor.role,
                    is_verified=doctor.is_verified,
                    is_active=doctor.is_active,
                    created_at=doctor.created_at,
                    plan=subscription.plan,
                    status=subscription.status,
                    used_today=usage_by_doctor.get(doctor.id, 0),
                    current_period_end=subscription.current_period_end,
                )
            )
        return rows

    async def override_plan(self, user_id: uuid.UUID, plan: SubscriptionPlan) -> AdminUserRead:
        subscription = await self._subscriptions.get_by_user_id(user_id)
        if subscription is None:
            subscription = await self._subscriptions.create(user_id=user_id, plan=plan)
        else:
            subscription.plan = plan
        await self._session.commit()
        await self._session.refresh(subscription)
        return await self.get_admin_user_read(user_id)

    async def get_admin_user_read(self, user_id: uuid.UUID) -> AdminUserRead:
        user = await self._users.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        subscription = await self.get_or_create_for_user(user)
        used_today = await self._prescriptions.count_since_for_doctor(user.id, _start_of_today_utc())
        return AdminUserRead(
            id=user.id,
            email=user.email,
            role=user.role,
            is_verified=user.is_verified,
            is_active=user.is_active,
            created_at=user.created_at,
            plan=subscription.plan,
            status=subscription.status,
            used_today=used_today,
            current_period_end=subscription.current_period_end,
        )


def _require_doctor(user: User) -> None:
    if user.role != UserRole.DOCTOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only doctor accounts have a subscription")


def _start_of_today_utc() -> datetime:
    return datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)


def _map_stripe_status(stripe_status: str) -> SubscriptionStatus:
    mapping = {
        "active": SubscriptionStatus.ACTIVE,
        "past_due": SubscriptionStatus.PAST_DUE,
        "canceled": SubscriptionStatus.CANCELED,
        "incomplete": SubscriptionStatus.INCOMPLETE,
        "incomplete_expired": SubscriptionStatus.CANCELED,
        "trialing": SubscriptionStatus.TRIALING,
        "unpaid": SubscriptionStatus.PAST_DUE,
    }
    return mapping.get(stripe_status, SubscriptionStatus.ACTIVE)
