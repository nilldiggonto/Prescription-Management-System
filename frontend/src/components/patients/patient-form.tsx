"use client";

import { Controller, useForm, type UseFormReturn } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import { Field, FieldError, FieldGroup, FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { patientSchema, type PatientFormValues } from "@/lib/validation";

export function usePatientForm(defaultValues?: Partial<PatientFormValues>) {
  return useForm<PatientFormValues>({
    resolver: zodResolver(patientSchema),
    defaultValues: {
      full_name: "",
      age: "",
      gender: undefined,
      phone: "",
      address: "",
      ...defaultValues,
    },
  });
}

interface PatientFormFieldsProps {
  form: UseFormReturn<PatientFormValues>;
}

export function PatientFormFields({ form }: PatientFormFieldsProps) {
  const {
    register,
    control,
    formState: { errors },
  } = form;

  return (
    <FieldGroup>
      <Field data-invalid={!!errors.full_name}>
        <FieldLabel htmlFor="patient_full_name">Patient name</FieldLabel>
        <Input id="patient_full_name" {...register("full_name")} />
        <FieldError errors={[errors.full_name]} />
      </Field>

      <div className="grid grid-cols-2 gap-4">
        <Field data-invalid={!!errors.age}>
          <FieldLabel htmlFor="patient_age">Age</FieldLabel>
          <Input id="patient_age" type="number" min={0} max={150} {...register("age")} />
          <FieldError errors={[errors.age]} />
        </Field>

        <Field data-invalid={!!errors.gender}>
          <FieldLabel htmlFor="patient_gender">Gender</FieldLabel>
          <Controller
            name="gender"
            control={control}
            render={({ field }) => (
              <Select value={field.value} onValueChange={field.onChange}>
                <SelectTrigger id="patient_gender" className="w-full">
                  <SelectValue placeholder="Select gender" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="male">Male</SelectItem>
                  <SelectItem value="female">Female</SelectItem>
                  <SelectItem value="other">Other</SelectItem>
                </SelectContent>
              </Select>
            )}
          />
          <FieldError errors={[errors.gender]} />
        </Field>
      </div>

      <Field data-invalid={!!errors.phone}>
        <FieldLabel htmlFor="patient_phone">Phone</FieldLabel>
        <Input id="patient_phone" {...register("phone")} />
        <FieldError errors={[errors.phone]} />
      </Field>

      <Field data-invalid={!!errors.address}>
        <FieldLabel htmlFor="patient_address">Address</FieldLabel>
        <Input id="patient_address" {...register("address")} />
        <FieldError errors={[errors.address]} />
      </Field>
    </FieldGroup>
  );
}
