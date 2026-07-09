import uuid
from datetime import datetime

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
