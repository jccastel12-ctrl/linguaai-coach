import "server-only";

import type { BillingOverview, PaymentCapabilities, PlanInfo } from "@/types";
import { backendFetch, getSessionToken } from "@/lib/server-auth";

export async function getPlans(): Promise<PlanInfo[]> {
  try {
    const response = await backendFetch("/api/v1/billing/plans");
    if (!response.ok) return [];
    return (await response.json()) as PlanInfo[];
  } catch {
    return [];
  }
}

export async function getBillingOverview(): Promise<BillingOverview | null> {
  const token = await getSessionToken();
  if (!token) return null;
  try {
    const response = await backendFetch("/api/v1/billing/me", {}, token);
    if (!response.ok) return null;
    return (await response.json()) as BillingOverview;
  } catch {
    return null;
  }
}


export async function getPaymentCapabilities(): Promise<PaymentCapabilities | null> {
  try {
    const response = await backendFetch("/api/v1/billing/payment-capabilities");
    if (!response.ok) return null;
    return (await response.json()) as PaymentCapabilities;
  } catch {
    return null;
  }
}
