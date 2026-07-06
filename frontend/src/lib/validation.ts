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
