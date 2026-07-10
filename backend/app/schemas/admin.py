import uuid
from datetime import date, datetime

from pydantic import BaseModel

from app.models.subscription import SubscriptionPlan, SubscriptionStatus
from app.models.user import UserRole


class AdminUserRead(BaseModel):
    id: uuid.UUID
    email: str
    role: UserRole
    is_verified: bool
    is_active: bool
    created_at: datetime
    plan: SubscriptionPlan
    status: SubscriptionStatus
    used_today: int
    current_period_end: datetime | None


class AdminSubscriptionUpdate(BaseModel):
    plan: SubscriptionPlan


class AdminStatusUpdate(BaseModel):
    is_active: bool


class DailyCount(BaseModel):
    date: date
    count: int


class AdminStats(BaseModel):
    total_doctors: int
    active_doctors: int
    suspended_doctors: int
    unverified_doctors: int
    plan_counts: dict[SubscriptionPlan, int]
    prescriptions_today: int
    prescriptions_total: int
    signups_last_14_days: list[DailyCount]
    prescriptions_last_14_days: list[DailyCount]
