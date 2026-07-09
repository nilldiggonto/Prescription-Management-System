from app.models.subscription import SubscriptionPlan

# Fixed product-tier definitions (not admin-configurable data) — keep in sync with the
# landing page copy (frontend/src/components/marketing/pricing-section.tsx).
PLAN_DAILY_LIMITS: dict[SubscriptionPlan, int | None] = {
    SubscriptionPlan.FREE: 20,
    SubscriptionPlan.PRO: 100,
    SubscriptionPlan.PREMIUM: None,  # unlimited
}
