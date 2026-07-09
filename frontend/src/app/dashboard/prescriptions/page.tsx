"use client";

import * as React from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { FilePlus2Icon, FileTextIcon, XIcon } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { ComingSoon } from "@/components/dashboard/coming-soon";
import { apiFetch } from "@/lib/api";
import type { Prescription } from "@/lib/types";

function PrescriptionsPageContent() {
  const searchParams = useSearchParams();
  const patientId = searchParams.get("patient_id");
  const patientName = searchParams.get("patient_name");

  const [prescriptions, setPrescriptions] = React.useState<Prescription[] | null>(null);

  React.useEffect(() => {
    // Resetting to a loading state when the patient filter changes, before re-fetching —
    // synchronizing with the external API, which is exactly what effects are for.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setPrescriptions(null);
    const path = patientId ? `/prescriptions?patient_id=${patientId}` : "/prescriptions";
    void apiFetch<Prescription[]>(path).then(setPrescriptions);
  }, [patientId]);

  return (
    <div>
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight">
            {patientId && patientName ? `Prescriptions for ${patientName}` : "Prescriptions"}
          </h2>
          <p className="mt-1 text-sm text-muted-foreground">
            {patientId ? (
              <Link href="/dashboard/prescriptions" className="inline-flex items-center gap-1 underline underline-offset-4">
                <XIcon className="size-3" />
                Clear filter, show everyone
              </Link>
            ) : (
              "Every prescription you've created."
            )}
          </p>
        </div>
        <Button render={<Link href="/dashboard/prescriptions/new" />}>
          <FilePlus2Icon />
          New Prescription
        </Button>
      </div>

      <div className="mt-6">
        {prescriptions === null ? (
          <p className="text-sm text-muted-foreground">Loading…</p>
        ) : prescriptions.length === 0 ? (
          <ComingSoon
            icon={FileTextIcon}
            title={patientId ? "No prescriptions for this patient yet" : "No prescriptions yet"}
            description="Create a prescription to see it here."
          />
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Patient</TableHead>
                <TableHead>Diagnosis</TableHead>
                <TableHead>Date</TableHead>
                <TableHead className="sr-only">View</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {prescriptions.map((prescription) => (
                <TableRow key={prescription.id}>
                  <TableCell className="font-medium">{prescription.patient.full_name}</TableCell>
                  <TableCell className="max-w-xs truncate">{prescription.diagnosis ?? "—"}</TableCell>
                  <TableCell>{new Date(prescription.created_at).toLocaleDateString()}</TableCell>
                  <TableCell>
                    <Button
                      variant="outline"
                      size="sm"
                      render={<Link href={`/dashboard/prescriptions/${prescription.id}`} />}
                    >
                      View
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </div>
    </div>
  );
}

export default function PrescriptionsPage() {
  return (
    <React.Suspense fallback={<p className="text-sm text-muted-foreground">Loading…</p>}>
      <PrescriptionsPageContent />
    </React.Suspense>
  );
}
