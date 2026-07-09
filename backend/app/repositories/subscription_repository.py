import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subscription import Subscription, SubscriptionPlan


class SubscriptionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_user_id(self, user_id: uuid.UUID) -> Subscription | None:
        result = await self._session.execute(select(Subscription).where(Subscription.user_id == user_id))
        return result.scalar_one_or_none()

    async def get_by_stripe_subscription_id(self, stripe_subscription_id: str) -> Subscription | None:
        result = await self._session.execute(
            select(Subscription).where(Subscription.stripe_subscription_id == stripe_subscription_id)
        )
        return result.scalar_one_or_none()

    async def create(self, *, user_id: uuid.UUID, plan: SubscriptionPlan = SubscriptionPlan.FREE) -> Subscription:
        subscription = Subscription(user_id=user_id, plan=plan)
        self._session.add(subscription)
        await self._session.flush()
        return subscription

    async def get_by_user_ids(self, user_ids: list[uuid.UUID]) -> dict[uuid.UUID, Subscription]:
        if not user_ids:
            return {}
        result = await self._session.execute(select(Subscription).where(Subscription.user_id.in_(user_ids)))
        return {subscription.user_id: subscription for subscription in result.scalars().all()}
