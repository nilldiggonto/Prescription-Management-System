import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SubscriptionPlan(str, Enum):
    FREE = "free"
    PRO = "pro"
    PREMIUM = "premium"


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    INCOMPLETE = "incomplete"
    TRIALING = "trialing"


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    plan: Mapped[SubscriptionPlan] = mapped_column(
        String(20), default=SubscriptionPlan.FREE, server_default=SubscriptionPlan.FREE.value, nullable=False
    )
    status: Mapped[SubscriptionStatus] = mapped_column(
        String(20),
        default=SubscriptionStatus.ACTIVE,
        server_default=SubscriptionStatus.ACTIVE.value,
        nullable=False,
    )
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    current_period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
