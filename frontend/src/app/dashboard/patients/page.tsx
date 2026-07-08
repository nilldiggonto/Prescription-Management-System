"use client";

import * as React from "react";
import Link from "next/link";
import { PlusIcon, UsersIcon } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { ComingSoon } from "@/components/dashboard/coming-soon";
import { apiFetch } from "@/lib/api";
import type { Patient } from "@/lib/types";

export default function PatientsPage() {
  const [patients, setPatients] = React.useState<Patient[] | null>(null);

  React.useEffect(() => {
    void apiFetch<Patient[]>("/patients").then(setPatients);
  }, []);

  return (
    <div>
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight">Patients</h2>
          <p className="mt-1 text-sm text-muted-foreground">Saved for reference when creating prescriptions.</p>
        </div>
        <Button render={<Link href="/dashboard/patients/new" />}>
          <PlusIcon />
          Add patient
        </Button>
      </div>

      <div className="mt-6">
        {patients === null ? (
          <p className="text-sm text-muted-foreground">Loading…</p>
        ) : patients.length === 0 ? (
          <ComingSoon
            icon={UsersIcon}
            title="No patients yet"
            description="Add your first patient, or create one directly while writing a prescription."
          />
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Age</TableHead>
                <TableHead>Gender</TableHead>
                <TableHead>Phone</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {patients.map((patient) => (
                <TableRow key={patient.id}>
                  <TableCell className="font-medium">{patient.full_name}</TableCell>
                  <TableCell>{patient.age ?? "—"}</TableCell>
                  <TableCell className="capitalize">{patient.gender}</TableCell>
                  <TableCell>{patient.phone ?? "—"}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </div>
    </div>
  );
}
