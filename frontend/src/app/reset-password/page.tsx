import { AuthCard } from "@/components/auth/auth-card";
import { ResetPasswordForm } from "@/components/auth/reset-password-form";

interface ResetPasswordPageProps {
  searchParams: Promise<{ email?: string }>;
}

export default async function ResetPasswordPage({ searchParams }: ResetPasswordPageProps) {
  const { email } = await searchParams;

  return (
    <AuthCard title="Reset your password" description="Enter the code we sent you and choose a new password.">
      <ResetPasswordForm defaultEmail={email ?? ""} />
    </AuthCard>
  );
}
