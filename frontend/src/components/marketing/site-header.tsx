"use client";

import Link from "next/link";
import { MenuIcon, Stethoscope } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { ThemeToggle } from "@/components/theme-toggle";
import { useAuth } from "@/lib/auth-context";

const NAV_LINKS = [
  { href: "#features", label: "Features" },
  { href: "#how-it-works", label: "How it works" },
  { href: "#pricing", label: "Pricing" },
  { href: "#faq", label: "FAQ" },
];

function Logo() {
  return (
    <Link href="/" className="flex items-center gap-2 font-heading font-semibold">
      <span className="flex size-7 items-center justify-center rounded-lg bg-primary text-primary-foreground">
        <Stethoscope className="size-4" />
      </span>
      Rivet
    </Link>
  );
}

function AuthButtons({ fullWidth = false }: { fullWidth?: boolean }) {
  const { user, isLoading, logout } = useAuth();

  if (isLoading) {
    return (
      <div className={fullWidth ? "flex flex-col gap-2" : "flex items-center gap-2"}>
        <div className="h-8 w-20 animate-pulse rounded-md bg-muted" />
        <div className="h-8 w-28 animate-pulse rounded-md bg-muted" />
      </div>
    );
  }

  if (user) {
    return (
      <div className={fullWidth ? "flex flex-col gap-2" : "flex items-center gap-2"}>
        <Button variant="outline" render={<Link href="/dashboard" />}>
          Dashboard
        </Button>
        <Button onClick={() => void logout()}>Log out</Button>
      </div>
    );
  }

  return (
    <div className={fullWidth ? "flex flex-col gap-2" : "flex items-center gap-2"}>
      <Button variant={fullWidth ? "outline" : "ghost"} render={<Link href="/login" />}>
        Sign in
      </Button>
      <Button render={<Link href="/register" />}>Get Started Free</Button>
    </div>
  );
}

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-40 w-full border-b bg-background/80 backdrop-blur supports-backdrop-filter:bg-background/60">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Logo />

        <nav className="hidden items-center gap-8 md:flex">
          {NAV_LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
            >
              {link.label}
            </a>
          ))}
        </nav>

        <div className="hidden items-center gap-2 md:flex">
          <ThemeToggle />
          <AuthButtons />
        </div>

        <div className="flex items-center gap-1 md:hidden">
          <ThemeToggle />
          <Sheet>
            <SheetTrigger
              render={<Button variant="ghost" size="icon" aria-label="Open menu" />}
            >
              <MenuIcon />
            </SheetTrigger>
            <SheetContent side="right" className="w-72">
              <SheetHeader>
                <SheetTitle>
                  <Logo />
                </SheetTitle>
              </SheetHeader>
              <nav className="flex flex-col gap-1 px-4">
                {NAV_LINKS.map((link) => (
                  <a
                    key={link.href}
                    href={link.href}
                    className="rounded-md px-2 py-2.5 text-sm font-medium text-foreground hover:bg-muted"
                  >
                    {link.label}
                  </a>
                ))}
              </nav>
              <div className="mt-auto p-4">
                <AuthButtons fullWidth />
              </div>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </header>
  );
}
