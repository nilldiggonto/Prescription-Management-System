import { FileTextIcon } from "lucide-react";

import { ComingSoon } from "@/components/dashboard/coming-soon";

export default function PrescriptionsPage() {
  return (
    <ComingSoon
      icon={FileTextIcon}
      title="Prescription history is coming soon"
      description="Once you start creating prescriptions, they'll show up here for reference."
    />
  );
}
