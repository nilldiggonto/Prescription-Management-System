from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

from app.models.subscription import SubscriptionPlan, SubscriptionStatus


class SubscriptionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    plan: SubscriptionPlan
    status: SubscriptionStatus
    daily_limit: int | None
    used_today: int
    current_period_end: datetime | None


class CheckoutRequest(BaseModel):
    plan: Literal[SubscriptionPlan.PRO, SubscriptionPlan.PREMIUM]


class CheckoutResponse(BaseModel):
    checkout_url: str


class PortalResponse(BaseModel):
    portal_url: str
