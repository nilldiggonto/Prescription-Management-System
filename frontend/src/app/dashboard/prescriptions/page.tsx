"use client";

import * as React from "react";
import Link from "next/link";
import { FilePlus2Icon, FileTextIcon } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { ComingSoon } from "@/components/dashboard/coming-soon";
import { apiFetch } from "@/lib/api";
import type { Prescription } from "@/lib/types";

export default function PrescriptionsPage() {
  const [prescriptions, setPrescriptions] = React.useState<Prescription[] | null>(null);

  React.useEffect(() => {
    void apiFetch<Prescription[]>("/prescriptions").then(setPrescriptions);
  }, []);

  return (
    <div>
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight">Prescriptions</h2>
          <p className="mt-1 text-sm text-muted-foreground">Every prescription you&apos;ve created.</p>
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
            title="No prescriptions yet"
            description="Create your first prescription to see it here."
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
