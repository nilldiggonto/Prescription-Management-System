"use client";

import * as React from "react";
import { useRouter } from "next/navigation";

import { AdminHeader } from "@/components/admin/admin-header";
import { useAuth } from "@/lib/auth-context";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { user, isLoading } = useAuth();

  React.useEffect(() => {
    if (!isLoading && !user) {
      router.push("/login");
    } else if (!isLoading && user?.role !== "admin") {
      router.push("/dashboard");
    }
  }, [isLoading, user, router]);

  if (isLoading || !user || user.role !== "admin") {
    return (
      <div className="flex min-h-svh flex-1 items-center justify-center text-sm text-muted-foreground">
        Loading…
      </div>
    );
  }

  return (
    <div className="flex min-h-svh flex-col">
      <AdminHeader />
      <main className="flex-1 p-4 md:p-6">{children}</main>
    </div>
  );
}
