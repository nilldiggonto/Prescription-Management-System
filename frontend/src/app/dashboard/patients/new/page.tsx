"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { PatientFormFields, usePatientForm } from "@/components/patients/patient-form";
import { apiFetch, ApiError } from "@/lib/api";
import { patientAgeToNumber, type PatientFormValues } from "@/lib/validation";
import type { Patient } from "@/lib/types";

export default function NewPatientPage() {
  const router = useRouter();
  const form = usePatientForm();
  const [rootError, setRootError] = React.useState<string | null>(null);

  async function onSubmit(values: PatientFormValues) {
    setRootError(null);
    try {
      const payload = {
        ...values,
        age: patientAgeToNumber(values.age),
        phone: values.phone || null,
        address: values.address || null,
      };
      await apiFetch<Patient>("/patients", { method: "POST", csrf: true, body: payload });
      toast.success("Patient added");
      router.push("/dashboard/patients");
    } catch (error) {
      setRootError(error instanceof ApiError ? error.message : "Something went wrong. Please try again.");
    }
  }

  return (
    <div className="max-w-lg">
      <h2 className="text-2xl font-semibold tracking-tight">Add patient</h2>
      <p className="mt-1 text-sm text-muted-foreground">Patient records are kept for reference on future prescriptions.</p>

      <form onSubmit={form.handleSubmit(onSubmit)} noValidate className="mt-6">
        <PatientFormFields form={form} />

        {rootError && (
          <p role="alert" className="mt-4 text-sm text-destructive">
            {rootError}
          </p>
        )}

        <Button type="submit" disabled={form.formState.isSubmitting} className="mt-4">
          {form.formState.isSubmitting ? "Saving…" : "Add patient"}
        </Button>
      </form>
    </div>
  );
}
