import "server-only";

import type { AdminAuditEvent, AdminOverview, AdminUserList } from "@/types";
import { backendFetch, getSessionToken } from "@/lib/server-auth";

async function adminFetch<T>(path: string): Promise<T | null> {
  const token = await getSessionToken();
  if (!token) return null;
  try {
    const response = await backendFetch(path, {}, token);
    if (!response.ok) return null;
    return (await response.json()) as T;
  } catch {
    return null;
  }
}

export async function getAdminOverview(): Promise<AdminOverview | null> {
  return adminFetch<AdminOverview>("/api/v1/admin/overview");
}

export async function getAdminUsers(search?: string): Promise<AdminUserList | null> {
  const params = new URLSearchParams({ limit: "100", offset: "0" });
  if (search) params.set("search", search);
  return adminFetch<AdminUserList>(`/api/v1/admin/users?${params.toString()}`);
}

export async function getPendingUpgrades(): Promise<AdminUserList | null> {
  return adminFetch<AdminUserList>("/api/v1/admin/users?upgrade_requests_only=true&limit=100&offset=0");
}

export async function getAdminAudit(): Promise<AdminAuditEvent[]> {
  return (await adminFetch<AdminAuditEvent[]>("/api/v1/admin/audit?limit=20")) ?? [];
}
