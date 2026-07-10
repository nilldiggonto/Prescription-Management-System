"use client";

import * as React from "react";
import { useSearchParams } from "next/navigation";
import { CheckIcon, CreditCardIcon, TriangleAlertIcon } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useSubscription } from "@/lib/subscription-context";
import { apiFetch, ApiError } from "@/lib/api";
import { PLAN_LABELS, STATUS_LABELS, type SubscriptionPlan } from "@/lib/types";
import { cn } from "@/lib/utils";

interface Tier {
  plan: SubscriptionPlan;
  price: string;
  cadence: string;
  description: string;
  limit: string;
  features: string[];
  highlighted?: boolean;
}

const TIERS: Tier[] = [
  {
    plan: "free",
    price: "$0",
    cadence: "/month",
    description: "Try Rivet with everything you need to get started.",
    limit: "20 prescriptions / day",
    features: ["1 doctor account", "Standard prescription theme", "Patient management", "Community support"],
  },
  {
    plan: "pro",
    price: "$29",
    cadence: "/month",
    description: "For busy practices that need more room to grow.",
    limit: "100 prescriptions / day",
    features: ["Everything in Free", "All prescription themes", "Patient history export", "Priority email support"],
    highlighted: true,
  },
  {
    plan: "premium",
    price: "$79",
    cadence: "/month",
    description: "For high-volume clinics that never want to think about limits.",
    limit: "Unlimited prescriptions",
    features: ["Everything in Pro", "Custom clinic branding", "Multiple doctor seats", "Dedicated support"],
  },
];

function BillingPageContent() {
  const searchParams = useSearchParams();
  const { subscription, isLoading, refresh } = useSubscription();
  const [pendingPlan, setPendingPlan] = React.useState<SubscriptionPlan | null>(null);
  const [isPortalLoading, setIsPortalLoading] = React.useState(false);

  React.useEffect(() => {
    const checkout = searchParams.get("checkout");
    const sessionId = searchParams.get("session_id");
    if (checkout === "success") {
      if (sessionId) {
        // Reconcile eagerly against Stripe using the Checkout Session ID rather than just
        // re-fetching our DB — the webhook that would normally do this update may not have
        // been delivered yet (or at all, if no webhook listener is running locally).
        apiFetch("/billing/sync-checkout", { method: "POST", csrf: true, body: { session_id: sessionId } })
          .then(() => {
            toast.success("Subscription updated — thanks!");
            void refresh();
          })
          .catch(() => {
            toast.success("Payment received — refreshing your plan…");
            void refresh();
          });
      } else {
        toast.success("Subscription updated — thanks!");
        void refresh();
      }
    } else if (checkout === "cancel") {
      toast.info("Checkout canceled — you're still on your previous plan.");
    }
    // Only react to the query params changing, not every `refresh` identity change.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  async function handleUpgrade(plan: "pro" | "premium") {
    setPendingPlan(plan);
    try {
      const { checkout_url } = await apiFetch<{ checkout_url: string }>("/billing/checkout", {
        method: "POST",
        csrf: true,
        body: { plan },
      });
      // Navigating away to Stripe Checkout — a browser API call, not a React state
      // mutation; the compiler's immutability check doesn't know `window.location` is safe.
      // eslint-disable-next-line react-hooks/immutability
      window.location.href = checkout_url;
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : "Couldn't start checkout. Please try again.");
      setPendingPlan(null);
    }
  }

  async function handleManageBilling() {
    setIsPortalLoading(true);
    try {
      const { portal_url } = await apiFetch<{ portal_url: string }>("/billing/portal", {
        method: "POST",
        csrf: true,
      });
      window.location.href = portal_url;
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : "Couldn't open billing portal.");
      setIsPortalLoading(false);
    }
  }

  if (isLoading || !subscription) {
    return <p className="text-sm text-muted-foreground">Loading…</p>;
  }

  return (
    <div>
      <div>
        <h2 className="text-2xl font-semibold tracking-tight">Billing</h2>
        <p className="mt-1 text-sm text-muted-foreground">Manage your subscription and see today&apos;s usage.</p>
      </div>

      <div className="mt-6 rounded-xl border bg-card p-6">
        {subscription.plan !== "free" && subscription.status !== "active" && (
          <div className="mb-4 flex items-start gap-2 rounded-lg bg-destructive/10 p-3 text-sm text-destructive">
            <TriangleAlertIcon className="mt-0.5 size-4 shrink-0" />
            <span>
              {subscription.status === "past_due"
                ? "Your last payment failed. Update your payment method to avoid losing access to your plan."
                : `Your subscription is ${STATUS_LABELS[subscription.status].toLowerCase()}.`}{" "}
              <button
                type="button"
                onClick={() => void handleManageBilling()}
                className="font-medium underline underline-offset-2"
              >
                Manage billing
              </button>
            </span>
          </div>
        )}
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="flex size-9 items-center justify-center rounded-full bg-primary/10 text-primary">
                <CreditCardIcon className="size-4" />
              </span>
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-heading text-lg font-semibold">
                    {subscription.plan === "free" ? "Free plan" : `${PLAN_LABELS[subscription.plan]} plan`}
                  </span>
                  {subscription.plan !== "free" && subscription.status === "active" && (
                    <Badge variant="secondary">Active</Badge>
                  )}
                </div>
                {subscription.plan !== "free" && subscription.current_period_end && (
                  <p className="text-xs text-muted-foreground">
                    Renews on{" "}
                    {new Date(subscription.current_period_end).toLocaleDateString(undefined, {
                      year: "numeric",
                      month: "long",
                      day: "numeric",
                    })}
                  </p>
                )}
              </div>
            </div>
          </div>
          {subscription.plan !== "free" && (
            <Button variant="outline" onClick={() => void handleManageBilling()} disabled={isPortalLoading}>
              {isPortalLoading ? "Opening…" : "Manage billing"}
            </Button>
          )}
        </div>

        <div className="mt-5 border-t pt-4">
          <p className="text-2xl font-semibold tracking-tight">
            {subscription.used_today}
            {subscription.daily_limit !== null && (
              <span className="text-base font-normal text-muted-foreground"> / {subscription.daily_limit}</span>
            )}
            <span className="ml-2 text-sm font-normal text-muted-foreground">
              prescriptions today{subscription.daily_limit === null && " (unlimited)"}
            </span>
          </p>
          {subscription.daily_limit !== null && (
            <div className="mt-3 h-2 w-full overflow-hidden rounded-full bg-muted">
              <div
                className="h-full rounded-full bg-primary transition-all"
                style={{
                  width: `${Math.min(100, (subscription.used_today / subscription.daily_limit) * 100)}%`,
                }}
              />
            </div>
          )}
        </div>
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-3">
        {TIERS.map((tier) => {
          const isCurrent = tier.plan === subscription.plan;
          return (
            <div
              key={tier.plan}
              className={cn(
                "flex flex-col rounded-xl border bg-card p-6",
                tier.highlighted && "border-primary shadow-lg ring-1 ring-primary/20"
              )}
            >
              <div className="flex items-center justify-between">
                <h3 className="font-heading text-lg font-semibold">{PLAN_LABELS[tier.plan]}</h3>
                {isCurrent && <Badge>Current plan</Badge>}
              </div>
              <p className="mt-2 text-sm text-muted-foreground">{tier.description}</p>
              <div className="mt-6 flex items-baseline gap-1">
                <span className="text-4xl font-semibold tracking-tight">{tier.price}</span>
                <span className="text-sm text-muted-foreground">{tier.cadence}</span>
              </div>
              <p className="mt-1 text-sm font-medium text-primary">{tier.limit}</p>
              <ul className="mt-6 flex flex-1 flex-col gap-2.5">
                {tier.features.map((feature) => (
                  <li key={feature} className="flex items-start gap-2 text-sm">
                    <CheckIcon className="mt-0.5 size-4 shrink-0 text-primary" />
                    <span className="text-muted-foreground">{feature}</span>
                  </li>
                ))}
              </ul>

              {tier.plan === "free" ? (
                <Button className="mt-8" variant="outline" disabled>
                  {isCurrent ? "Current plan" : "Downgrade via billing portal"}
                </Button>
              ) : isCurrent ? (
                <Button className="mt-8" variant="outline" disabled>
                  Current plan
                </Button>
              ) : (
                <Button
                  className="mt-8"
                  variant={tier.highlighted ? "default" : "outline"}
                  disabled={pendingPlan !== null}
                  onClick={() => void handleUpgrade(tier.plan as "pro" | "premium")}
                >
                  {pendingPlan === tier.plan ? "Redirecting…" : `Upgrade to ${PLAN_LABELS[tier.plan]}`}
                </Button>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default function BillingPage() {
  return (
    <React.Suspense fallback={<p className="text-sm text-muted-foreground">Loading…</p>}>
      <BillingPageContent />
    </React.Suspense>
  );
}
