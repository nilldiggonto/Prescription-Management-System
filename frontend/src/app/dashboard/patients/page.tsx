import { UsersIcon } from "lucide-react";

import { ComingSoon } from "@/components/dashboard/coming-soon";

export default function PatientsPage() {
  return (
    <ComingSoon
      icon={UsersIcon}
      title="Patient records are coming soon"
      description="Patients you prescribe to will be saved here for future reference."
    />
  );
}
