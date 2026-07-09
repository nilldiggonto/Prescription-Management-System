"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  ChevronsUpDownIcon,
  CreditCardIcon,
  FilePlus2Icon,
  FileTextIcon,
  LayoutDashboardIcon,
  LogOutIcon,
  SettingsIcon,
  Stethoscope,
  UsersIcon,
} from "lucide-react";

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/lib/auth-context";
import { useSubscription } from "@/lib/subscription-context";
import { PLAN_LABELS } from "@/lib/types";

const NAV_PRESCRIPTIONS = [
  { href: "/dashboard/prescriptions/new", label: "New Prescription", icon: FilePlus2Icon },
  { href: "/dashboard/prescriptions", label: "All Prescriptions", icon: FileTextIcon },
];

const NAV_RECORDS = [{ href: "/dashboard/patients", label: "Patients", icon: UsersIcon }];

function initials(email: string) {
  return email.slice(0, 2).toUpperCase();
}

export function AppSidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const { subscription } = useSubscription();

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg" render={<Link href="/dashboard" />}>
              <span className="flex size-7 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                <Stethoscope className="size-4" />
              </span>
              <span className="font-heading font-semibold">Rivet</span>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton
                  isActive={pathname === "/dashboard"}
                  tooltip="Dashboard"
                  render={<Link href="/dashboard" />}
                >
                  <LayoutDashboardIcon />
                  <span>Dashboard</span>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarGroup>
          <SidebarGroupLabel>Prescriptions</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {NAV_PRESCRIPTIONS.map((item) => (
                <SidebarMenuItem key={item.href}>
                  <SidebarMenuButton
                    isActive={pathname === item.href}
                    tooltip={item.label}
                    render={<Link href={item.href} />}
                  >
                    <item.icon />
                    <span>{item.label}</span>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarGroup>
          <SidebarGroupLabel>Records</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {NAV_RECORDS.map((item) => (
                <SidebarMenuItem key={item.href}>
                  <SidebarMenuButton
                    isActive={pathname === item.href}
                    tooltip={item.label}
                    render={<Link href={item.href} />}
                  >
                    <item.icon />
                    <span>{item.label}</span>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarGroup>
          <SidebarGroupLabel>Account</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton
                  isActive={pathname === "/dashboard/billing"}
                  tooltip="Billing"
                  render={<Link href="/dashboard/billing" />}
                >
                  <CreditCardIcon />
                  <span>Billing</span>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton
                  isActive={pathname === "/dashboard/settings"}
                  tooltip="Settings"
                  render={<Link href="/dashboard/settings" />}
                >
                  <SettingsIcon />
                  <span>Settings</span>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter>
        <SidebarMenu>
          <SidebarMenuItem>
            <DropdownMenu>
              <DropdownMenuTrigger
                render={
                  <SidebarMenuButton size="lg">
                    <Avatar size="sm" className="rounded-md">
                      <AvatarFallback className="rounded-md">
                        {user ? initials(user.email) : "?"}
                      </AvatarFallback>
                    </Avatar>
                    <div className="grid flex-1 text-left leading-tight">
                      <span className="truncate text-sm font-medium">{user?.email}</span>
                      <span className="mt-0.5 flex items-center gap-1.5 truncate text-xs text-muted-foreground">
                        <span className="capitalize">{user?.role}</span>
                        {subscription && (
                          <Badge variant="outline" className="h-4 px-1.5 text-[10px]">
                            {PLAN_LABELS[subscription.plan]}
                          </Badge>
                        )}
                      </span>
                    </div>
                    <ChevronsUpDownIcon className="ml-auto size-4 text-muted-foreground" />
                  </SidebarMenuButton>
                }
              />
              <DropdownMenuContent side="top" align="start" className="w-(--anchor-width) min-w-56">
                <DropdownMenuItem render={<Link href="/dashboard/settings" />}>
                  <SettingsIcon />
                  Settings
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem variant="destructive" onClick={() => void logout()}>
                  <LogOutIcon />
                  Log out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
    </Sidebar>
  );
}
