"use client";

import Link from "next/link";
import { LogOutIcon, ShieldIcon } from "lucide-react";

import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/theme-toggle";
import { useAuth } from "@/lib/auth-context";

export function AdminHeader() {
  const { user, logout } = useAuth();

  return (
    <header className="sticky top-0 z-40 flex h-14 items-center justify-between border-b bg-background/80 px-4 backdrop-blur">
      <Link href="/admin" className="flex items-center gap-2 font-heading font-semibold">
        <span className="flex size-7 items-center justify-center rounded-lg bg-primary text-primary-foreground">
          <ShieldIcon className="size-4" />
        </span>
        Rivet Admin
      </Link>

      <div className="flex items-center gap-3">
        <span className="hidden text-sm text-muted-foreground sm:inline">{user?.email}</span>
        <ThemeToggle />
        <Button variant="outline" size="sm" onClick={() => void logout()}>
          <LogOutIcon />
          Log out
        </Button>
      </div>
    </header>
  );
}
