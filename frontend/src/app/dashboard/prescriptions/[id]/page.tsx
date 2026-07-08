"use client";

import * as React from "react";
import { useParams } from "next/navigation";
import { PrinterIcon } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { PrescriptionPadFrame, PrescriptionRxLabel } from "@/components/prescriptions/prescription-pad";
import { apiFetch } from "@/lib/api";
import type { DoctorProfile, Prescription } from "@/lib/types";

function formatDate(value: string) {
  return new Date(value).toLocaleDateString(undefined, { day: "2-digit", month: "short", year: "numeric" });
}

export default function PrescriptionViewPage() {
  const { id } = useParams<{ id: string }>();
  const [prescription, setPrescription] = React.useState<Prescription | null>(null);
  const [doctorProfile, setDoctorProfile] = React.useState<DoctorProfile | null>(null);

  React.useEffect(() => {
    void apiFetch<Prescription>(`/prescriptions/${id}`).then(setPrescription);
    void apiFetch<DoctorProfile>("/doctor-profile/me").then(setDoctorProfile);
  }, [id]);

  if (!prescription || !doctorProfile) {
    return <p className="text-sm text-muted-foreground">Loading…</p>;
  }

  const { patient } = prescription;

  return (
    <div className="mx-auto max-w-3xl">
      <div className="flex justify-end print:hidden">
        <Button onClick={() => window.print()}>
          <PrinterIcon />
          Print / Save as PDF
        </Button>
      </div>

      <div className="mt-4 print:mt-0">
        <PrescriptionPadFrame doctorProfile={doctorProfile}>
          <div className="flex items-start justify-between border-b pb-3 text-sm">
            <div className="space-x-4">
              <span>
                <span className="font-medium">Patient:</span> {patient.full_name}
              </span>
              {patient.age !== null && (
                <span>
                  <span className="font-medium">Age:</span> {patient.age}
                </span>
              )}
              <span className="capitalize">
                <span className="font-medium">Gender:</span> {patient.gender}
              </span>
              {patient.phone && (
                <span>
                  <span className="font-medium">Phone:</span> {patient.phone}
                </span>
              )}
            </div>
            <span>
              <span className="font-medium">Date:</span> {formatDate(prescription.created_at)}
            </span>
          </div>

          {prescription.diagnosis && (
            <div className="border-b py-3">
              <h2 className="text-sm font-semibold text-muted-foreground">Diagnosis</h2>
              <p className="mt-1 text-sm whitespace-pre-line">{prescription.diagnosis}</p>
            </div>
          )}

          <div className="py-4">
            <PrescriptionRxLabel template={doctorProfile.template} />
            <Table className="mt-2">
              <TableHeader>
                <TableRow>
                  <TableHead>Medicine</TableHead>
                  <TableHead>Dosage</TableHead>
                  <TableHead>Frequency</TableHead>
                  <TableHead>Duration</TableHead>
                  <TableHead>Instructions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {prescription.medicines.map((medicine) => (
                  <TableRow key={medicine.id}>
                    <TableCell className="font-medium">{medicine.name}</TableCell>
                    <TableCell>{medicine.dosage}</TableCell>
                    <TableCell>{medicine.frequency}</TableCell>
                    <TableCell>{medicine.duration}</TableCell>
                    <TableCell>{medicine.instructions ?? "—"}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>

          {prescription.advice && (
            <div className="border-t py-3">
              <h2 className="text-sm font-semibold text-muted-foreground">Advice</h2>
              <p className="mt-1 text-sm whitespace-pre-line">{prescription.advice}</p>
            </div>
          )}

          {prescription.follow_up_date && (
            <div className="border-t py-3">
              <h2 className="text-sm font-semibold text-muted-foreground">Follow-up</h2>
              <p className="mt-1 text-sm">{formatDate(prescription.follow_up_date)}</p>
            </div>
          )}

          <div className="flex justify-end pt-8">
            <div className="text-center text-sm">
              <div className="w-48 border-t border-foreground/60 pt-1">
                {doctorProfile.full_name}
                <br />
                Reg. No: {doctorProfile.registration_number}
              </div>
            </div>
          </div>
        </PrescriptionPadFrame>
      </div>
    </div>
  );
}
