"use client";

import * as React from "react";
import { useRouter } from "next/navigation";

import { apiFetch } from "@/lib/api";

export interface CurrentUser {
  id: string;
  email: string;
  role: "doctor" | "admin";
  is_verified: boolean;
  is_active: boolean;
  created_at: string;
}

interface AuthContextValue {
  user: CurrentUser | null;
  isLoading: boolean;
  refresh: () => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = React.createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [user, setUser] = React.useState<CurrentUser | null>(null);
  const [isLoading, setIsLoading] = React.useState(true);

  const refresh = React.useCallback(async () => {
    try {
      const currentUser = await apiFetch<CurrentUser>("/auth/me");
      setUser(currentUser);
    } catch {
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  React.useEffect(() => {
    // Fetching the current session from the backend on mount — synchronizing
    // with an external system (the API), which is exactly what effects are for.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void refresh();
  }, [refresh]);

  const logout = React.useCallback(async () => {
    try {
      await apiFetch("/auth/logout", { method: "POST", csrf: true });
    } catch {
      // Even if the request fails, clear local state so the UI doesn't get stuck logged-in.
    }
    setUser(null);
    router.push("/");
  }, [router]);

  const value = React.useMemo(
    () => ({ user, isLoading, refresh, logout }),
    [user, isLoading, refresh, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = React.useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
