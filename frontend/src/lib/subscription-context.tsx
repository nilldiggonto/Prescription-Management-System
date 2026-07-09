"use client";

import * as React from "react";

import { apiFetch } from "@/lib/api";
import type { Subscription } from "@/lib/types";

interface SubscriptionContextValue {
  subscription: Subscription | null;
  isLoading: boolean;
  refresh: () => Promise<void>;
}

const SubscriptionContext = React.createContext<SubscriptionContextValue | undefined>(undefined);

export function SubscriptionProvider({ children }: { children: React.ReactNode }) {
  const [subscription, setSubscription] = React.useState<Subscription | null>(null);
  const [isLoading, setIsLoading] = React.useState(true);

  const refresh = React.useCallback(async () => {
    try {
      const current = await apiFetch<Subscription>("/billing/me");
      setSubscription(current);
    } catch {
      setSubscription(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  React.useEffect(() => {
    // Fetching the current subscription on mount — synchronizing with the external
    // API, which is exactly what effects are for.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void refresh();
  }, [refresh]);

  const value = React.useMemo(() => ({ subscription, isLoading, refresh }), [subscription, isLoading, refresh]);

  return <SubscriptionContext.Provider value={value}>{children}</SubscriptionContext.Provider>;
}

export function useSubscription(): SubscriptionContextValue {
  const context = React.useContext(SubscriptionContext);
  if (!context) {
    throw new Error("useSubscription must be used within a SubscriptionProvider");
  }
  return context;
}
