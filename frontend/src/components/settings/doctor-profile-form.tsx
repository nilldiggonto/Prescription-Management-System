"use client";

import * as React from "react";
import { Controller, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { toast } from "sonner";
import { CheckIcon } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Field, FieldDescription, FieldError, FieldGroup, FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import { doctorProfileSchema, type DoctorProfileFormValues } from "@/lib/validation";
import { apiFetch, ApiError } from "@/lib/api";
import type { DoctorProfile, PrescriptionTemplate } from "@/lib/types";
import { PrescriptionPadFrame, PrescriptionRxLabel } from "@/components/prescriptions/prescription-pad";

const EMPTY_VALUES: DoctorProfileFormValues = {
  full_name: "",
  degrees: "",
  specialization: "",
  registration_number: "",
  hospital_name: "",
  chamber_address: "",
  phone: "",
  signature_url: "",
  logo_url: "",
  watermark_url: "",
  template: "classic",
};

const TEMPLATE_OPTIONS: { value: PrescriptionTemplate; label: string; description: string }[] = [
  { value: "classic", label: "Classic", description: "Centered header, formal double rule" },
  { value: "modern", label: "Modern", description: "Colored accent bar, logo beside your name" },
  { value: "minimal", label: "Minimal", description: "Small header, lots of whitespace" },
];

function toFormValues(profile: DoctorProfile): DoctorProfileFormValues {
  return {
    full_name: profile.full_name,
    degrees: profile.degrees,
    specialization: profile.specialization ?? "",
    registration_number: profile.registration_number,
    hospital_name: profile.hospital_name ?? "",
    chamber_address: profile.chamber_address ?? "",
    phone: profile.phone ?? "",
    signature_url: profile.signature_url ?? "",
    logo_url: profile.logo_url ?? "",
    watermark_url: profile.watermark_url ?? "",
    template: profile.template,
  };
}

export function DoctorProfileForm() {
  const [isLoading, setIsLoading] = React.useState(true);
  const [rootError, setRootError] = React.useState<string | null>(null);

  const {
    register,
    control,
    handleSubmit,
    reset,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<DoctorProfileFormValues>({
    resolver: zodResolver(doctorProfileSchema),
    defaultValues: EMPTY_VALUES,
  });

  const preview = watch();

  React.useEffect(() => {
    let cancelled = false;

    async function loadProfile() {
      try {
        const profile = await apiFetch<DoctorProfile>("/doctor-profile/me");
        if (!cancelled) reset(toFormValues(profile));
      } catch (error) {
        if (!(error instanceof ApiError) || error.status !== 404) {
          toast.error("Couldn't load your doctor profile. Please refresh the page.");
        }
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    void loadProfile();
    return () => {
      cancelled = true;
    };
  }, [reset]);

  async function onSubmit(values: DoctorProfileFormValues) {
    setRootError(null);
    try {
      const profile = await apiFetch<DoctorProfile>("/doctor-profile/me", {
        method: "PUT",
        csrf: true,
        body: {
          ...values,
          specialization: values.specialization || null,
          hospital_name: values.hospital_name || null,
          chamber_address: values.chamber_address || null,
          phone: values.phone || null,
          signature_url: values.signature_url || null,
          logo_url: values.logo_url || null,
          watermark_url: values.watermark_url || null,
        },
      });
      reset(toFormValues(profile));
      toast.success("Doctor profile saved");
    } catch (error) {
      setRootError(error instanceof ApiError ? error.message : "Something went wrong. Please try again.");
    }
  }

  if (isLoading) {
    return <p className="text-sm text-muted-foreground">Loading your profile…</p>;
  }

  return (
    <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_minmax(0,420px)]">
      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        <FieldGroup>
          <FieldDescription>
            This information appears as the letterhead on every prescription you create.
          </FieldDescription>

          <Field>
            <FieldLabel>Prescription template</FieldLabel>
            <Controller
              name="template"
              control={control}
              render={({ field }) => (
                <div className="grid grid-cols-1 gap-2 sm:grid-cols-3">
                  {TEMPLATE_OPTIONS.map((option) => (
                    <button
                      key={option.value}
                      type="button"
                      onClick={() => field.onChange(option.value)}
                      className={cn(
                        "flex flex-col items-start gap-1 rounded-lg border p-3 text-left transition-colors hover:bg-muted",
                        field.value === option.value ? "border-primary ring-1 ring-primary" : "border-border"
                      )}
                    >
                      <span className="flex w-full items-center justify-between text-sm font-medium">
                        {option.label}
                        {field.value === option.value && <CheckIcon className="size-4 text-primary" />}
                      </span>
                      <span className="text-xs text-muted-foreground">{option.description}</span>
                    </button>
                  ))}
                </div>
              )}
            />
          </Field>

          <Field data-invalid={!!errors.full_name}>
            <FieldLabel htmlFor="full_name">Full name</FieldLabel>
            <Input id="full_name" placeholder="Dr. Jane Doe" {...register("full_name")} />
            <FieldError errors={[errors.full_name]} />
          </Field>

          <Field data-invalid={!!errors.degrees}>
            <FieldLabel htmlFor="degrees">Degrees</FieldLabel>
            <Input id="degrees" placeholder="MBBS, FCPS (Medicine)" {...register("degrees")} />
            <FieldError errors={[errors.degrees]} />
          </Field>

          <Field data-invalid={!!errors.specialization}>
            <FieldLabel htmlFor="specialization">Specialization</FieldLabel>
            <Input id="specialization" placeholder="Cardiologist" {...register("specialization")} />
            <FieldError errors={[errors.specialization]} />
          </Field>

          <Field data-invalid={!!errors.registration_number}>
            <FieldLabel htmlFor="registration_number">Registration number</FieldLabel>
            <Input id="registration_number" placeholder="A-12345" {...register("registration_number")} />
            <FieldError errors={[errors.registration_number]} />
          </Field>

          <Field data-invalid={!!errors.hospital_name}>
            <FieldLabel htmlFor="hospital_name">Hospital / clinic name</FieldLabel>
            <Input id="hospital_name" {...register("hospital_name")} />
            <FieldError errors={[errors.hospital_name]} />
          </Field>

          <Field data-invalid={!!errors.chamber_address}>
            <FieldLabel htmlFor="chamber_address">Chamber address</FieldLabel>
            <Input id="chamber_address" {...register("chamber_address")} />
            <FieldError errors={[errors.chamber_address]} />
          </Field>

          <Field data-invalid={!!errors.phone}>
            <FieldLabel htmlFor="phone">Phone</FieldLabel>
            <Input id="phone" {...register("phone")} />
            <FieldError errors={[errors.phone]} />
          </Field>

          <Field data-invalid={!!errors.logo_url}>
            <FieldLabel htmlFor="logo_url">Clinic logo URL</FieldLabel>
            <Input id="logo_url" placeholder="https://…" {...register("logo_url")} />
            <FieldError errors={[errors.logo_url]} />
          </Field>

          <Field data-invalid={!!errors.watermark_url}>
            <FieldLabel htmlFor="watermark_url">Watermark image URL</FieldLabel>
            <Input id="watermark_url" placeholder="https://…" {...register("watermark_url")} />
            <FieldDescription>Optional. A faint background image shown behind the prescription.</FieldDescription>
            <FieldError errors={[errors.watermark_url]} />
          </Field>

          <Field data-invalid={!!errors.signature_url}>
            <FieldLabel htmlFor="signature_url">Signature image URL</FieldLabel>
            <Input id="signature_url" placeholder="https://…" {...register("signature_url")} />
            <FieldDescription>
              Optional. Direct upload isn&apos;t supported yet — paste a hosted image URL.
            </FieldDescription>
            <FieldError errors={[errors.signature_url]} />
          </Field>

          {rootError && (
            <p role="alert" className="text-sm text-destructive">
              {rootError}
            </p>
          )}

          <Button type="submit" disabled={isSubmitting} className="w-fit">
            {isSubmitting ? "Saving…" : "Save profile"}
          </Button>
        </FieldGroup>
      </form>

      <div>
        <p className="mb-2 text-sm font-medium text-muted-foreground">Live preview</p>
        <div className="sticky top-6 origin-top-left scale-[0.85]">
          <PrescriptionPadFrame doctorProfile={preview} className="text-sm shadow-sm">
            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <span>Patient: Jane Sample (34, Female)</span>
              <span>Date: 01 Jan 2026</span>
            </div>
            <div className="mt-3">
              <PrescriptionRxLabel template={preview.template} />
              <p className="mt-1 text-xs text-muted-foreground">Paracetamol 500mg — 1+1+1 — 5 days</p>
            </div>
          </PrescriptionPadFrame>
        </div>
      </div>
    </div>
  );
}
