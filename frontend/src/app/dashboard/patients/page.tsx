"use client";

import * as React from "react";
import Link from "next/link";
import { FileTextIcon, PhoneIcon, SearchIcon, UsersIcon } from "lucide-react";

import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { ComingSoon } from "@/components/dashboard/coming-soon";
import { apiFetch } from "@/lib/api";
import type { Patient } from "@/lib/types";

function initials(name: string) {
  return name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join("");
}

export default function PatientsPage() {
  const [patients, setPatients] = React.useState<Patient[] | null>(null);
  const [search, setSearch] = React.useState("");

  React.useEffect(() => {
    void apiFetch<Patient[]>("/patients").then(setPatients);
  }, []);

  const filteredPatients = React.useMemo(() => {
    if (!patients) return null;
    const query = search.trim().toLowerCase();
    if (!query) return patients;
    return patients.filter(
      (patient) =>
        patient.full_name.toLowerCase().includes(query) || (patient.phone ?? "").toLowerCase().includes(query)
    );
  }, [patients, search]);

  return (
    <div>
      <div>
        <h2 className="text-2xl font-semibold tracking-tight">Patients</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Saved automatically when you create a prescription for someone new.
        </p>
      </div>

      {patients !== null && patients.length > 0 && (
        <div className="relative mt-4 max-w-sm">
          <SearchIcon className="absolute top-1/2 left-2.5 size-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search by name or phone…"
            className="pl-8"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </div>
      )}

      <div className="mt-6">
        {patients === null ? (
          <p className="text-sm text-muted-foreground">Loading…</p>
        ) : patients.length === 0 ? (
          <ComingSoon
            icon={UsersIcon}
            title="No patients yet"
            description="Patients are added automatically the first time you write them a prescription."
          />
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Patient</TableHead>
                <TableHead>Age</TableHead>
                <TableHead>Gender</TableHead>
                <TableHead className="sr-only">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredPatients?.map((patient) => (
                <TableRow key={patient.id}>
                  <TableCell>
                    <div className="flex items-center gap-3">
                      <Avatar size="sm">
                        <AvatarFallback>{initials(patient.full_name)}</AvatarFallback>
                      </Avatar>
                      <div>
                        <p className="font-medium">{patient.full_name}</p>
                        {patient.phone && (
                          <p className="flex items-center gap-1 text-xs text-muted-foreground">
                            <PhoneIcon className="size-3" />
                            {patient.phone}
                          </p>
                        )}
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>{patient.age ?? "—"}</TableCell>
                  <TableCell className="capitalize">{patient.gender}</TableCell>
                  <TableCell className="text-right">
                    <Button
                      variant="outline"
                      size="sm"
                      render={
                        <Link
                          href={`/dashboard/prescriptions?patient_id=${patient.id}&patient_name=${encodeURIComponent(patient.full_name)}`}
                        />
                      }
                    >
                      <FileTextIcon />
                      Prescriptions
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
              {filteredPatients?.length === 0 && (
                <TableRow>
                  <TableCell colSpan={4} className="text-center text-sm text-muted-foreground">
                    No patients match &quot;{search}&quot;.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        )}
      </div>
    </div>
  );
}
