"use client";

import * as React from "react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { apiFetch, ApiError } from "@/lib/api";
import { PLAN_LABELS, type AdminUser, type SubscriptionPlan } from "@/lib/types";

const PLAN_OPTIONS: SubscriptionPlan[] = ["free", "pro", "premium"];

export default function AdminUsersPage() {
  const [users, setUsers] = React.useState<AdminUser[] | null>(null);
  const [pendingUserId, setPendingUserId] = React.useState<string | null>(null);

  const loadUsers = React.useCallback(async () => {
    try {
      const data = await apiFetch<AdminUser[]>("/admin/users");
      setUsers(data);
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : "Couldn't load users.");
    }
  }, []);

  React.useEffect(() => {
    // Fetching the user list on mount — synchronizing with the external API, which is
    // exactly what effects are for.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void loadUsers();
  }, [loadUsers]);

  async function handlePlanChange(userId: string, plan: SubscriptionPlan) {
    setPendingUserId(userId);
    try {
      const updated = await apiFetch<AdminUser>(`/admin/users/${userId}/subscription`, {
        method: "PATCH",
        csrf: true,
        body: { plan },
      });
      setUsers((current) => current?.map((user) => (user.id === userId ? updated : user)) ?? null);
      toast.success(`Plan updated to ${PLAN_LABELS[plan]}`);
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : "Couldn't update plan.");
    } finally {
      setPendingUserId(null);
    }
  }

  async function handleToggleActive(user: AdminUser) {
    setPendingUserId(user.id);
    try {
      const updated = await apiFetch<AdminUser>(`/admin/users/${user.id}/status`, {
        method: "PATCH",
        csrf: true,
        body: { is_active: !user.is_active },
      });
      setUsers((current) => current?.map((u) => (u.id === user.id ? updated : u)) ?? null);
      toast.success(updated.is_active ? "Account reactivated" : "Account suspended");
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : "Couldn't update account status.");
    } finally {
      setPendingUserId(null);
    }
  }

  return (
    <div>
      <h2 className="text-2xl font-semibold tracking-tight">Doctors</h2>
      <p className="mt-1 text-sm text-muted-foreground">
        View every doctor account, override their plan, or suspend access.
      </p>

      <div className="mt-6">
        {users === null ? (
          <p className="text-sm text-muted-foreground">Loading…</p>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Email</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Plan</TableHead>
                <TableHead>Used today</TableHead>
                <TableHead>Joined</TableHead>
                <TableHead className="sr-only">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {users.map((user) => (
                <TableRow key={user.id}>
                  <TableCell className="font-medium">
                    {user.email}
                    {!user.is_verified && (
                      <Badge variant="outline" className="ml-2">
                        Unverified
                      </Badge>
                    )}
                  </TableCell>
                  <TableCell>
                    <Badge variant={user.is_active ? "secondary" : "destructive"}>
                      {user.is_active ? "Active" : "Suspended"}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Select
                      value={user.plan}
                      onValueChange={(value) => void handlePlanChange(user.id, value as SubscriptionPlan)}
                      disabled={pendingUserId === user.id}
                    >
                      <SelectTrigger size="sm" className="w-28">
                        <SelectValue>{PLAN_LABELS[user.plan]}</SelectValue>
                      </SelectTrigger>
                      <SelectContent>
                        {PLAN_OPTIONS.map((plan) => (
                          <SelectItem key={plan} value={plan}>
                            {PLAN_LABELS[plan]}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </TableCell>
                  <TableCell>{user.used_today}</TableCell>
                  <TableCell>{new Date(user.created_at).toLocaleDateString()}</TableCell>
                  <TableCell className="text-right">
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={pendingUserId === user.id}
                      onClick={() => void handleToggleActive(user)}
                    >
                      {user.is_active ? "Suspend" : "Reactivate"}
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
              {users.length === 0 && (
                <TableRow>
                  <TableCell colSpan={6} className="text-center text-sm text-muted-foreground">
                    No doctors yet.
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
