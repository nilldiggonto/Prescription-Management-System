"use client";

import * as React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Controller, useFieldArray, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import { FilePlus2Icon, PlusIcon, Trash2Icon } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Field, FieldError, FieldGroup, FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ComingSoon } from "@/components/dashboard/coming-soon";
import { PrescriptionPadFrame, PrescriptionRxLabel } from "@/components/prescriptions/prescription-pad";
import { medicineItemSchema, patientAgeToNumber } from "@/lib/validation";
import { apiFetch, ApiError } from "@/lib/api";
import type { DoctorProfile, Patient, Prescription } from "@/lib/types";

const prescriptionFormSchema = z.object({
  patient_id: z.string().optional(),
  new_patient: z.object({
    full_name: z.string().optional(),
    age: z
      .string()
      .regex(/^\d{0,3}$/, "Enter a valid age")
      .optional()
      .or(z.literal("")),
    gender: z.enum(["male", "female", "other"]).optional(),
    phone: z.string().optional(),
    address: z.string().optional(),
  }),
  diagnosis: z.string().max(5000).optional().or(z.literal("")),
  advice: z.string().max(5000).optional().or(z.literal("")),
  follow_up_date: z.string().optional().or(z.literal("")),
  medicines: z.array(medicineItemSchema).min(1, "Add at least one medicine"),
});

type PrescriptionFormValues = z.infer<typeof prescriptionFormSchema>;

const EMPTY_MEDICINE = { name: "", dosage: "", frequency: "", duration: "", instructions: "" };

export default function NewPrescriptionPage() {
  const router = useRouter();
  const [doctorProfile, setDoctorProfile] = React.useState<DoctorProfile | null>(null);
  const [profileMissing, setProfileMissing] = React.useState(false);
  const [patientMode, setPatientMode] = React.useState<"existing" | "new">("existing");
  const [patients, setPatients] = React.useState<Patient[] | null>(null);
  const [rootError, setRootError] = React.useState<React.ReactNode>(null);

  React.useEffect(() => {
    void apiFetch<Patient[]>("/patients").then(setPatients);
    apiFetch<DoctorProfile>("/doctor-profile/me")
      .then(setDoctorProfile)
      .catch((error) => {
        if (error instanceof ApiError && error.status === 404) setProfileMissing(true);
      });
  }, []);

  const {
    register,
    control,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<PrescriptionFormValues>({
    resolver: zodResolver(prescriptionFormSchema),
    defaultValues: {
      patient_id: "",
      new_patient: { full_name: "", age: "", gender: undefined, phone: "", address: "" },
      diagnosis: "",
      advice: "",
      follow_up_date: "",
      medicines: [EMPTY_MEDICINE],
    },
  });

  const { fields, append, remove } = useFieldArray({ control, name: "medicines" });

  async function onSubmit(values: PrescriptionFormValues) {
    setRootError(null);

    if (patientMode === "existing" && !values.patient_id) {
      setError("patient_id", { message: "Select a patient" });
      return;
    }
    if (patientMode === "new") {
      if (!values.new_patient.full_name) {
        setError("new_patient.full_name", { message: "Patient name is required" });
        return;
      }
      if (!values.new_patient.gender) {
        setError("new_patient.gender", { message: "Select a gender" });
        return;
      }
    }

    const payload = {
      ...(patientMode === "existing"
        ? { patient_id: values.patient_id }
        : {
            new_patient: {
              full_name: values.new_patient.full_name,
              age: patientAgeToNumber(values.new_patient.age),
              gender: values.new_patient.gender,
              phone: values.new_patient.phone || null,
              address: values.new_patient.address || null,
            },
          }),
      diagnosis: values.diagnosis || null,
      advice: values.advice || null,
      follow_up_date: values.follow_up_date || null,
      medicines: values.medicines.map((medicine) => ({ ...medicine, instructions: medicine.instructions || null })),
    };

    try {
      const prescription = await apiFetch<Prescription>("/prescriptions", {
        method: "POST",
        csrf: true,
        body: payload,
      });
      toast.success("Prescription created");
      router.push(`/dashboard/prescriptions/${prescription.id}`);
    } catch (error) {
      if (error instanceof ApiError && error.status === 400 && error.message.toLowerCase().includes("doctor profile")) {
        setProfileMissing(true);
        return;
      }
      setRootError(error instanceof ApiError ? error.message : "Something went wrong. Please try again.");
    }
  }

  if (profileMissing) {
    return (
      <div className="max-w-lg">
        <ComingSoon
          icon={FilePlus2Icon}
          title="Set up your doctor profile first"
          description="Your name, degrees, and registration number appear as the letterhead on every prescription."
        />
        <Button className="mt-4" render={<Link href="/dashboard/settings" />}>
          Go to settings
        </Button>
      </div>
    );
  }

  if (!doctorProfile) {
    return <p className="text-sm text-muted-foreground">Loading…</p>;
  }

  return (
    <div className="mx-auto max-w-3xl">
      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        <PrescriptionPadFrame doctorProfile={doctorProfile}>
          <div className="flex flex-wrap items-center justify-between gap-2 border-b pb-3">
            <div className="flex gap-2">
              <Button
                type="button"
                size="sm"
                variant={patientMode === "existing" ? "default" : "outline"}
                onClick={() => setPatientMode("existing")}
              >
                Existing patient
              </Button>
              <Button
                type="button"
                size="sm"
                variant={patientMode === "new" ? "default" : "outline"}
                onClick={() => setPatientMode("new")}
              >
                New patient
              </Button>
            </div>
            <Input type="date" className="w-auto" defaultValue={new Date().toISOString().slice(0, 10)} disabled />
          </div>

          <div className="border-b py-3">
            {patientMode === "existing" ? (
              <Field data-invalid={!!errors.patient_id}>
                <Controller
                  name="patient_id"
                  control={control}
                  render={({ field }) => (
                    <Select value={field.value} onValueChange={field.onChange}>
                      <SelectTrigger id="patient_id" className="w-full max-w-sm">
                        <SelectValue placeholder={patients === null ? "Loading patients…" : "Select a patient"} />
                      </SelectTrigger>
                      <SelectContent>
                        {patients?.map((patient) => (
                          <SelectItem key={patient.id} value={patient.id}>
                            {patient.full_name}
                            {patient.age ? ` (${patient.age})` : ""}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  )}
                />
                <FieldError errors={[errors.patient_id]} />
                {patients?.length === 0 && (
                  <p className="mt-1 text-sm text-muted-foreground">
                    No saved patients yet — switch to &quot;New patient&quot; above.
                  </p>
                )}
              </Field>
            ) : (
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                <Field className="col-span-2" data-invalid={!!errors.new_patient?.full_name}>
                  <FieldLabel htmlFor="new_patient_full_name">Patient name</FieldLabel>
                  <Input id="new_patient_full_name" {...register("new_patient.full_name")} />
                  <FieldError errors={[errors.new_patient?.full_name]} />
                </Field>
                <Field data-invalid={!!errors.new_patient?.age}>
                  <FieldLabel htmlFor="new_patient_age">Age</FieldLabel>
                  <Input id="new_patient_age" {...register("new_patient.age")} />
                  <FieldError errors={[errors.new_patient?.age]} />
                </Field>
                <Field data-invalid={!!errors.new_patient?.gender}>
                  <FieldLabel htmlFor="new_patient_gender">Gender</FieldLabel>
                  <Controller
                    name="new_patient.gender"
                    control={control}
                    render={({ field }) => (
                      <Select value={field.value} onValueChange={field.onChange}>
                        <SelectTrigger id="new_patient_gender" className="w-full">
                          <SelectValue placeholder="Select" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="male">Male</SelectItem>
                          <SelectItem value="female">Female</SelectItem>
                          <SelectItem value="other">Other</SelectItem>
                        </SelectContent>
                      </Select>
                    )}
                  />
                  <FieldError errors={[errors.new_patient?.gender]} />
                </Field>
                <Field>
                  <FieldLabel htmlFor="new_patient_phone">Phone</FieldLabel>
                  <Input id="new_patient_phone" {...register("new_patient.phone")} />
                </Field>
                <Field className="col-span-2 sm:col-span-3">
                  <FieldLabel htmlFor="new_patient_address">Address</FieldLabel>
                  <Input id="new_patient_address" {...register("new_patient.address")} />
                </Field>
              </div>
            )}
          </div>

          <div className="border-b py-4">
            {errors.diagnosis && <FieldError errors={[errors.diagnosis]} />}
            <FieldLabel htmlFor="diagnosis" className="text-muted-foreground">
              Diagnosis
            </FieldLabel>
            <Textarea
              id="diagnosis"
              rows={2}
              placeholder="—"
              className="mt-1 border-none px-0 shadow-none focus-visible:ring-0"
              {...register("diagnosis")}
            />
          </div>

          <div className="py-4">
            <div className="mb-2 flex items-center justify-between">
              <PrescriptionRxLabel template={doctorProfile.template} />
              {errors.medicines?.root && (
                <p className="text-sm text-destructive">{errors.medicines.root.message}</p>
              )}
            </div>

            <div className="space-y-3">
              {fields.map((field, index) => (
                <div key={field.id} className="flex flex-wrap items-start gap-2 border-b border-dashed pb-3">
                  <span className="mt-2.5 text-sm text-muted-foreground">{index + 1}.</span>
                  <Field className="min-w-[10rem] flex-1" data-invalid={!!errors.medicines?.[index]?.name}>
                    <Input placeholder="Medicine name" {...register(`medicines.${index}.name`)} />
                    <FieldError errors={[errors.medicines?.[index]?.name]} />
                  </Field>
                  <Field className="w-24" data-invalid={!!errors.medicines?.[index]?.dosage}>
                    <Input placeholder="Dosage" {...register(`medicines.${index}.dosage`)} />
                    <FieldError errors={[errors.medicines?.[index]?.dosage]} />
                  </Field>
                  <Field className="w-24" data-invalid={!!errors.medicines?.[index]?.frequency}>
                    <Input placeholder="1+1+1" {...register(`medicines.${index}.frequency`)} />
                    <FieldError errors={[errors.medicines?.[index]?.frequency]} />
                  </Field>
                  <Field className="w-24" data-invalid={!!errors.medicines?.[index]?.duration}>
                    <Input placeholder="Duration" {...register(`medicines.${index}.duration`)} />
                    <FieldError errors={[errors.medicines?.[index]?.duration]} />
                  </Field>
                  <Field className="min-w-[8rem] flex-1">
                    <Input placeholder="Instructions" {...register(`medicines.${index}.instructions`)} />
                  </Field>
                  {fields.length > 1 && (
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon-sm"
                      className="mt-1"
                      onClick={() => remove(index)}
                    >
                      <Trash2Icon />
                    </Button>
                  )}
                </div>
              ))}
            </div>

            <Button type="button" variant="ghost" size="sm" className="mt-2" onClick={() => append(EMPTY_MEDICINE)}>
              <PlusIcon />
              Add medicine
            </Button>
          </div>

          <div className="grid gap-4 border-t pt-4 sm:grid-cols-2">
            <Field>
              <FieldLabel htmlFor="advice" className="text-muted-foreground">
                Advice
              </FieldLabel>
              <Textarea
                id="advice"
                rows={2}
                placeholder="—"
                className="mt-1 border-none px-0 shadow-none focus-visible:ring-0"
                {...register("advice")}
              />
            </Field>
            <Field>
              <FieldLabel htmlFor="follow_up_date" className="text-muted-foreground">
                Follow-up date
              </FieldLabel>
              <Input id="follow_up_date" type="date" className="mt-1 w-fit" {...register("follow_up_date")} />
            </Field>
          </div>
        </PrescriptionPadFrame>

        {rootError && (
          <p role="alert" className="mt-4 text-sm text-destructive">
            {rootError}
          </p>
        )}

        <div className="mt-4 flex justify-end print:hidden">
          <Button type="submit" size="lg" disabled={isSubmitting}>
            {isSubmitting ? "Creating…" : "Create prescription"}
          </Button>
        </div>
      </form>
    </div>
  );
}
