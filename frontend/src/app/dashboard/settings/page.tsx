import { DoctorProfileForm } from "@/components/settings/doctor-profile-form";

export default function SettingsPage() {
  return (
    <div>
      <h2 className="text-2xl font-semibold tracking-tight">Doctor profile</h2>
      <p className="mt-1 text-sm text-muted-foreground">
        Set this up once — it&apos;s used as the letterhead on every prescription you create.
      </p>
      <div className="mt-6">
        <DoctorProfileForm />
      </div>
    </div>
  );
}
