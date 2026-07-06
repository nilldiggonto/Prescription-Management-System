"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { LogOutIcon } from "lucide-react";

import { Button } from "@/components/ui/button";
import { useAuth } from "@/lib/auth-context";

export default function DashboardPage() {
  const router = useRouter();
  const { user, isLoading, logout } = useAuth();

  React.useEffect(() => {
    if (!isLoading && !user) {
      router.push("/login");
    }
  }, [isLoading, user, router]);

  if (isLoading || !user) {
    return (
      <div className="flex flex-1 items-center justify-center px-4 py-24 text-sm text-muted-foreground">
        Loading…
      </div>
    );
  }

  return (
    <div className="mx-auto flex w-full max-w-2xl flex-1 flex-col px-4 py-16">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Welcome back</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            This is a placeholder dashboard — patients and prescriptions come next.
          </p>
        </div>
        <Button variant="outline" onClick={() => void logout()}>
          <LogOutIcon />
          Log out
        </Button>
      </div>

      <div className="mt-8 rounded-xl border bg-card p-6">
        <h2 className="text-sm font-semibold text-muted-foreground">Signed in as</h2>
        <dl className="mt-4 grid grid-cols-[auto_1fr] gap-x-6 gap-y-3 text-sm">
          <dt className="text-muted-foreground">Email</dt>
          <dd className="font-medium">{user.email}</dd>
          <dt className="text-muted-foreground">Role</dt>
          <dd className="font-medium capitalize">{user.role}</dd>
          <dt className="text-muted-foreground">Email verified</dt>
          <dd className="font-medium">{user.is_verified ? "Yes" : "No"}</dd>
        </dl>
      </div>
    </div>
  );
}
