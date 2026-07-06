import { AuthCard } from "@/components/auth/auth-card";
import { VerifyEmailForm } from "@/components/auth/verify-email-form";

interface VerifyEmailPageProps {
  searchParams: Promise<{ email?: string }>;
}

export default async function VerifyEmailPage({ searchParams }: VerifyEmailPageProps) {
  const { email } = await searchParams;

  return (
    <AuthCard
      title="Verify your email"
      description="Enter the 6-digit code we sent to your inbox."
    >
      <VerifyEmailForm defaultEmail={email ?? ""} />
    </AuthCard>
  );
}
