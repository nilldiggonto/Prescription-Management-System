import { z } from "zod";

export const emailSchema = z.email("Enter a valid email address");

// Mirrors backend's _validate_password_strength (backend/app/schemas/auth.py)
export const passwordSchema = z
  .string()
  .min(8, "Password must be at least 8 characters")
  .max(128, "Password must be at most 128 characters")
  .refine((value) => /[a-zA-Z]/.test(value), "Password must contain at least one letter")
  .refine((value) => /\d/.test(value), "Password must contain at least one number");

export const otpSchema = z
  .string()
  .length(6, "Enter the 6-digit code")
  .regex(/^\d{6}$/, "Code must be 6 digits");

export const prescriptionTemplateSchema = z.enum(["classic", "modern", "minimal"]);

// Mirrors backend's DoctorProfileWrite (backend/app/schemas/doctor_profile.py)
export const doctorProfileSchema = z.object({
  full_name: z.string().min(1, "Full name is required").max(150),
  degrees: z.string().min(1, "Degrees are required").max(255),
  specialization: z.string().max(150).optional().or(z.literal("")),
  registration_number: z.string().min(1, "Registration number is required").max(100),
  hospital_name: z.string().max(200).optional().or(z.literal("")),
  chamber_address: z.string().max(500).optional().or(z.literal("")),
  phone: z.string().max(30).optional().or(z.literal("")),
  signature_url: z.string().max(500).optional().or(z.literal("")),
  logo_url: z.string().max(500).optional().or(z.literal("")),
  watermark_url: z.string().max(500).optional().or(z.literal("")),
  template: prescriptionTemplateSchema,
});

export type DoctorProfileFormValues = z.infer<typeof doctorProfileSchema>;

// Mirrors backend's PatientWrite (backend/app/schemas/patient.py). `age` is kept as a plain
// string here (not z.coerce'd to number) so the form's input/output types match exactly —
// zod v4 + @hookform/resolvers v5 can't type a resolver whose input/output types diverge.
// Callers convert "" -> null and the string -> Number(...) at submit time.
export const patientSchema = z.object({
  full_name: z.string().min(1, "Patient name is required").max(150),
  age: z
    .string()
    .regex(/^\d{0,3}$/, "Enter a valid age")
    .optional()
    .or(z.literal("")),
  gender: z.enum(["male", "female", "other"], { error: "Select a gender" }),
  phone: z.string().max(30).optional().or(z.literal("")),
  address: z.string().max(500).optional().or(z.literal("")),
});

export type PatientFormValues = z.infer<typeof patientSchema>;

export function patientAgeToNumber(age: string | undefined): number | null {
  return age ? Number(age) : null;
}

// Mirrors backend's MedicineItem (backend/app/schemas/prescription.py)
export const medicineItemSchema = z.object({
  name: z.string().min(1, "Medicine name is required").max(200),
  dosage: z.string().min(1, "Dosage is required").max(100),
  frequency: z.string().min(1, "Frequency is required").max(100),
  duration: z.string().min(1, "Duration is required").max(100),
  instructions: z.string().max(300).optional().or(z.literal("")),
});
