import { SettingsIcon } from "lucide-react";

import { ComingSoon } from "@/components/dashboard/coming-soon";

export default function SettingsPage() {
  return (
    <ComingSoon
      icon={SettingsIcon}
      title="Doctor profile settings are coming soon"
      description="Your name, clinic, and signature details will live here — used as the letterhead on every prescription you create."
    />
  );
}
