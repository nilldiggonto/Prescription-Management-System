export type PrescriptionTemplate = "classic" | "modern" | "minimal";

export interface DoctorProfile {
  id: string;
  full_name: string;
  degrees: string;
  specialization: string | null;
  registration_number: string;
  hospital_name: string | null;
  chamber_address: string | null;
  phone: string | null;
  signature_url: string | null;
  logo_url: string | null;
  watermark_url: string | null;
  template: PrescriptionTemplate;
  created_at: string;
  updated_at: string;
}

export type PatientGender = "male" | "female" | "other";

export const GENDER_LABELS: Record<PatientGender, string> = {
  male: "Male",
  female: "Female",
  other: "Other",
};

export interface Patient {
  id: string;
  full_name: string;
  age: number | null;
  gender: PatientGender;
  phone: string | null;
  address: string | null;
  created_at: string;
}

export function formatPatientOption(patient: Patient): string {
  return patient.phone ? `${patient.full_name} — ${patient.phone}` : patient.full_name;
}

export interface Medicine {
  id: string;
  name: string;
  dosage: string;
  frequency: string;
  duration: string;
  instructions: string | null;
}

export interface Prescription {
  id: string;
  patient: Patient;
  diagnosis: string | null;
  advice: string | null;
  follow_up_date: string | null;
  medicines: Medicine[];
  created_at: string;
}

export type SubscriptionPlan = "free" | "pro" | "premium";
export type SubscriptionStatus = "active" | "past_due" | "canceled" | "incomplete" | "trialing";

export const PLAN_LABELS: Record<SubscriptionPlan, string> = {
  free: "Free",
  pro: "Pro",
  premium: "Premium",
};

export interface Subscription {
  plan: SubscriptionPlan;
  status: SubscriptionStatus;
  daily_limit: number | null;
  used_today: number;
  current_period_end: string | null;
}

export interface AdminUser {
  id: string;
  email: string;
  role: "doctor" | "admin";
  is_verified: boolean;
  is_active: boolean;
  created_at: string;
  plan: SubscriptionPlan;
  status: SubscriptionStatus;
  used_today: number;
  current_period_end: string | null;
}
