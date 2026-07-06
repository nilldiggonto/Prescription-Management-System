"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { Controller, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Field, FieldLabel, FieldError, FieldGroup, FieldDescription } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { InputOTP, InputOTPGroup, InputOTPSlot } from "@/components/ui/input-otp";
import { emailSchema, otpSchema } from "@/lib/validation";
import { apiFetch, ApiError } from "@/lib/api";

const verifyEmailSchema = z.object({
  email: emailSchema,
  otp: otpSchema,
});

type VerifyEmailValues = z.infer<typeof verifyEmailSchema>;

export function VerifyEmailForm({ defaultEmail }: { defaultEmail: string }) {
  const router = useRouter();
  const [rootError, setRootError] = React.useState<string | null>(null);

  const {
    register,
    handleSubmit,
    control,
    formState: { errors, isSubmitting },
  } = useForm<VerifyEmailValues>({
    resolver: zodResolver(verifyEmailSchema),
    defaultValues: { email: defaultEmail, otp: "" },
  });

  async function onSubmit(values: VerifyEmailValues) {
    setRootError(null);
    try {
      await apiFetch("/auth/verify-email", { method: "POST", body: values });
      toast.success("Email verified — you can now sign in.");
      router.push("/login");
    } catch (error) {
      setRootError(error instanceof ApiError ? error.message : "Something went wrong. Please try again.");
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate>
      <FieldGroup>
        <Field data-invalid={!!errors.email}>
          <FieldLabel htmlFor="email">Email</FieldLabel>
          <Input id="email" type="email" autoComplete="email" {...register("email")} />
          <FieldError errors={[errors.email]} />
        </Field>

        <Field data-invalid={!!errors.otp}>
          <FieldLabel htmlFor="otp">Verification code</FieldLabel>
          <Controller
            name="otp"
            control={control}
            render={({ field }) => (
              <InputOTP maxLength={6} id="otp" value={field.value} onChange={field.onChange} onBlur={field.onBlur}>
                <InputOTPGroup>
                  {Array.from({ length: 6 }).map((_, index) => (
                    <InputOTPSlot key={index} index={index} />
                  ))}
                </InputOTPGroup>
              </InputOTP>
            )}
          />
          <FieldDescription>Check your inbox (and spam folder) for a 6-digit code.</FieldDescription>
          <FieldError errors={[errors.otp]} />
        </Field>

        {rootError && (
          <p role="alert" className="text-sm text-destructive">
            {rootError}
          </p>
        )}

        <Button type="submit" disabled={isSubmitting} className="mt-1 w-full">
          {isSubmitting ? "Verifying…" : "Verify email"}
        </Button>
      </FieldGroup>
    </form>
  );
}
