"use client";

import * as React from "react";
import { Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { CalendarPlusIcon, FileTextIcon, ShieldBanIcon, UsersIcon } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PLAN_LABELS, type AdminStats } from "@/lib/types";
import { cn } from "@/lib/utils";

function formatDay(dateString: string): string {
  return new Date(dateString).toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

function StatTile({
  label,
  value,
  icon: Icon,
  tone,
}: {
  label: string;
  value: number;
  icon: React.ComponentType<{ className?: string }>;
  tone?: "default" | "destructive";
}) {
  return (
    <Card size="sm">
      <CardContent className="flex items-center gap-3">
        <span
          className={cn(
            "flex size-9 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary",
            tone === "destructive" && "bg-destructive/10 text-destructive"
          )}
        >
          <Icon className="size-4" />
        </span>
        <div>
          <p className="text-2xl font-semibold tracking-tight">{value}</p>
          <p className="text-xs text-muted-foreground">{label}</p>
        </div>
      </CardContent>
    </Card>
  );
}

export function AdminStatsSection({ stats }: { stats: AdminStats | null }) {
  if (!stats) {
    return <p className="text-sm text-muted-foreground">Loading stats…</p>;
  }

  const planData = (Object.keys(PLAN_LABELS) as Array<keyof typeof PLAN_LABELS>).map((plan) => ({
    plan: PLAN_LABELS[plan],
    count: stats.plan_counts[plan] ?? 0,
  }));

  const signupsData = stats.signups_last_14_days.map((day) => ({ label: formatDay(day.date), count: day.count }));
  const prescriptionsData = stats.prescriptions_last_14_days.map((day) => ({
    label: formatDay(day.date),
    count: day.count,
  }));

  return (
    <div className="mb-8">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatTile label="Total doctors" value={stats.total_doctors} icon={UsersIcon} />
        <StatTile
          label="Active paid subscriptions"
          value={(stats.plan_counts.pro ?? 0) + (stats.plan_counts.premium ?? 0)}
          icon={CalendarPlusIcon}
        />
        <StatTile label="Suspended accounts" value={stats.suspended_doctors} icon={ShieldBanIcon} tone="destructive" />
        <StatTile label="Prescriptions today" value={stats.prescriptions_today} icon={FileTextIcon} />
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-3">
        <Card size="sm">
          <CardHeader>
            <CardTitle>Plan distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={180}>
              <BarChart data={planData}>
                <CartesianGrid vertical={false} stroke="var(--border)" />
                <XAxis dataKey="plan" tickLine={false} axisLine={false} fontSize={12} />
                <YAxis allowDecimals={false} tickLine={false} axisLine={false} fontSize={12} width={28} />
                <Tooltip
                  contentStyle={{
                    background: "var(--card)",
                    border: "1px solid var(--border)",
                    borderRadius: "8px",
                    fontSize: "12px",
                  }}
                />
                <Bar dataKey="count" fill="var(--color-chart-1)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card size="sm">
          <CardHeader>
            <CardTitle>New doctors (14 days)</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={180}>
              <LineChart data={signupsData}>
                <CartesianGrid vertical={false} stroke="var(--border)" />
                <XAxis dataKey="label" tickLine={false} axisLine={false} fontSize={11} interval={2} />
                <YAxis allowDecimals={false} tickLine={false} axisLine={false} fontSize={12} width={28} />
                <Tooltip
                  contentStyle={{
                    background: "var(--card)",
                    border: "1px solid var(--border)",
                    borderRadius: "8px",
                    fontSize: "12px",
                  }}
                />
                <Line type="monotone" dataKey="count" stroke="var(--color-chart-2)" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card size="sm">
          <CardHeader>
            <CardTitle>Prescriptions (14 days)</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={180}>
              <LineChart data={prescriptionsData}>
                <CartesianGrid vertical={false} stroke="var(--border)" />
                <XAxis dataKey="label" tickLine={false} axisLine={false} fontSize={11} interval={2} />
                <YAxis allowDecimals={false} tickLine={false} axisLine={false} fontSize={12} width={28} />
                <Tooltip
                  contentStyle={{
                    background: "var(--card)",
                    border: "1px solid var(--border)",
                    borderRadius: "8px",
                    fontSize: "12px",
                  }}
                />
                <Line type="monotone" dataKey="count" stroke="var(--color-chart-3)" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
