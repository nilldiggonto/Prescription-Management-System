"use client";

import * as React from "react";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { MailCheckIcon } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Field, FieldLabel, FieldError, FieldGroup } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { emailSchema } from "@/lib/validation";
import { apiFetch, ApiError } from "@/lib/api";

const forgotPasswordSchema = z.object({ email: emailSchema });

type ForgotPasswordValues = z.infer<typeof forgotPasswordSchema>;

export function ForgotPasswordForm() {
  const [submittedEmail, setSubmittedEmail] = React.useState<string | null>(null);
  const [rootError, setRootError] = React.useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ForgotPasswordValues>({ resolver: zodResolver(forgotPasswordSchema) });

  async function onSubmit(values: ForgotPasswordValues) {
    setRootError(null);
    try {
      await apiFetch("/auth/forgot-password", { method: "POST", body: values });
      setSubmittedEmail(values.email);
    } catch (error) {
      setRootError(error instanceof ApiError ? error.message : "Something went wrong. Please try again.");
    }
  }

  if (submittedEmail) {
    return (
      <div className="flex flex-col items-center text-center">
        <span className="flex size-10 items-center justify-center rounded-full bg-primary/10 text-primary">
          <MailCheckIcon className="size-5" />
        </span>
        <p className="mt-3 text-sm text-muted-foreground">
          If an account exists for <span className="font-medium text-foreground">{submittedEmail}</span>, a
          reset code is on its way.
        </p>
        <Button className="mt-6 w-full" render={
          <Link href={`/reset-password?email=${encodeURIComponent(submittedEmail)}`} />
        }>
          Enter reset code
        </Button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate>
      <FieldGroup>
        <Field data-invalid={!!errors.email}>
          <FieldLabel htmlFor="email">Email</FieldLabel>
          <Input id="email" type="email" autoComplete="email" placeholder="you@example.com" {...register("email")} />
          <FieldError errors={[errors.email]} />
        </Field>

        {rootError && (
          <p role="alert" className="text-sm text-destructive">
            {rootError}
          </p>
        )}

        <Button type="submit" disabled={isSubmitting} className="mt-1 w-full">
          {isSubmitting ? "Sending…" : "Send reset code"}
        </Button>
      </FieldGroup>

      <p className="mt-6 text-center text-sm text-muted-foreground">
        Remembered your password?{" "}
        <Link href="/login" className="font-medium text-foreground underline underline-offset-4">
          Sign in
        </Link>
      </p>
    </form>
  );
}
