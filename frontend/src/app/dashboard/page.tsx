"use client";

import Link from "next/link";
import { ClipboardListIcon, FilePlus2Icon, FileTextIcon, UsersIcon } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/lib/auth-context";

const STATS = [
  { label: "Prescriptions today", value: "0", icon: FileTextIcon },
  { label: "Total patients", value: "0", icon: UsersIcon },
  { label: "This month", value: "0", icon: ClipboardListIcon },
];

export default function DashboardPage() {
  const { user } = useAuth();
  const name = user?.email.split("@")[0] ?? "";

  return (
    <div className="mx-auto flex w-full max-w-5xl flex-1 flex-col gap-6">
      <div>
        <h2 className="text-2xl font-semibold tracking-tight capitalize">Welcome back, {name}</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Here&apos;s what&apos;s happening with your practice today.
        </p>
      </div>

      <Card className="border-primary/30 bg-primary/5">
        <CardContent className="flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center">
          <div className="flex items-start gap-4">
            <span className="flex size-11 shrink-0 items-center justify-center rounded-xl bg-primary text-primary-foreground">
              <FilePlus2Icon className="size-5" />
            </span>
            <div>
              <h3 className="font-heading text-base font-semibold">Create a new prescription</h3>
              <p className="mt-1 text-sm text-muted-foreground">
                Write a digital prescription for your patient and print it in seconds.
              </p>
            </div>
          </div>
          <Button size="lg" className="w-full shrink-0 sm:w-auto" render={<Link href="/dashboard/prescriptions/new" />}>
            New Prescription
          </Button>
        </CardContent>
      </Card>

      <div className="grid gap-4 sm:grid-cols-3">
        {STATS.map((stat) => (
          <Card key={stat.label}>
            <CardContent className="flex items-center gap-3">
              <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-muted">
                <stat.icon className="size-4 text-muted-foreground" />
              </span>
              <div>
                <p className="text-2xl font-semibold tracking-tight">{stat.value}</p>
                <p className="text-xs text-muted-foreground">{stat.label}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Recent prescriptions</CardTitle>
          <CardDescription>Your most recently created prescriptions will show up here.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center gap-3 rounded-lg border border-dashed py-12 text-center">
            <span className="flex size-10 items-center justify-center rounded-full bg-muted">
              <FileTextIcon className="size-5 text-muted-foreground" />
            </span>
            <div>
              <p className="text-sm font-medium">No prescriptions yet</p>
              <p className="mt-1 text-sm text-muted-foreground">
                Create your first prescription to see it here.
              </p>
            </div>
            <Button variant="outline" size="sm" render={<Link href="/dashboard/prescriptions/new" />}>
              Create prescription
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
