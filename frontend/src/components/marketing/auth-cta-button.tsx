"use client";

import type * as React from "react";
import Link from "next/link";

import { Button } from "@/components/ui/button";
import { useAuth } from "@/lib/auth-context";

type AuthCtaButtonProps = Omit<React.ComponentProps<typeof Button>, "render">;

export function AuthCtaButton({ children, ...props }: AuthCtaButtonProps) {
  const { user, isLoading } = useAuth();
  const href = user ? "/dashboard" : "/login";

  return (
    <Button {...props} disabled={isLoading || props.disabled} render={<Link href={href} />}>
      {children}
    </Button>
  );
}
