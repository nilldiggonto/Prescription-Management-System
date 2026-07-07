import { FilePlus2Icon } from "lucide-react";

import { ComingSoon } from "@/components/dashboard/coming-soon";

export default function NewPrescriptionPage() {
  return (
    <ComingSoon
      icon={FilePlus2Icon}
      title="The prescription builder is coming next"
      description="This is where you'll write and print a digital prescription for your patient."
    />
  );
}
