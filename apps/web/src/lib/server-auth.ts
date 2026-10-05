import "server-only";

import { cookies } from "next/headers";
import type { User } from "@/types";

export const SESSION_COOKIE = "linguaai_access_token";

function apiBaseUrl(): string {
  return process.env.API_INTERNAL_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
}

export async function getSessionToken(): Promise<string | null> {
  return (await cookies()).get(SESSION_COOKIE)?.value ?? null;
}

export async function setSessionToken(token: string, maxAgeSeconds: number): Promise<void> {
  (await cookies()).set(SESSION_COOKIE, token, {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: Math.max(60, maxAgeSeconds),
  });
}

export async function clearSessionToken(): Promise<void> {
  (await cookies()).set(SESSION_COOKIE, "", {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: 0,
  });
}

export async function backendFetch(path: string, init: RequestInit = {}, token?: string): Promise<Response> {
  const headers = new Headers(init.headers);
  headers.set("Accept", "application/json");
  if (init.body && !headers.has("Content-Type")) headers.set("Content-Type", "application/json");
  if (token) headers.set("Authorization", `Bearer ${token}`);

  return fetch(`${apiBaseUrl()}${path}`, {
    ...init,
    headers,
    cache: "no-store",
  });
}

export async function getCurrentUser(): Promise<User | null> {
  const token = await getSessionToken();
  if (!token) return null;

  try {
    const response = await backendFetch("/api/v1/auth/me", {}, token);
    if (!response.ok) return null;
    return (await response.json()) as User;
  } catch {
    return null;
  }
}

export async function readApiError(response: Response): Promise<string> {
  try {
    const payload = (await response.json()) as { detail?: unknown };
    if (typeof payload.detail === "string") return payload.detail;
    if (Array.isArray(payload.detail)) {
      return payload.detail
        .map((item) => {
          if (item && typeof item === "object" && "msg" in item) return String((item as { msg: unknown }).msg);
          return null;
        })
        .filter(Boolean)
        .join(". ");
    }
  } catch {
    // Fall through to a status-based message.
  }
  return `La solicitud no pudo completarse (${response.status}).`;
}
