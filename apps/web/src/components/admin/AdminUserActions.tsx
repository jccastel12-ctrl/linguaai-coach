"use client";

import { useState } from "react";
import type { PlanTier } from "@/types";

interface Props {
  userId: string;
  currentPlan: PlanTier;
  requestedPlan: PlanTier | null;
  isActive: boolean;
  isSelf: boolean;
}

export function AdminUserActions({ userId, currentPlan, requestedPlan, isActive, isSelf }: Props) {
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  async function updatePlan(plan_tier: PlanTier) {
    setBusy(true);
    setMessage(null);
    try {
      const response = await fetch(`/api/session/admin/users/${userId}/subscription`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          plan_tier,
          status: "active",
          note: requestedPlan === "pro" && plan_tier === "pro" ? "Solicitud Pro aprobada manualmente" : "Cambio manual desde el panel web",
        }),
      });
      const payload = (await response.json()) as { detail?: string };
      if (!response.ok) throw new Error(payload.detail ?? "No fue posible actualizar el plan.");
      window.location.reload();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "No fue posible actualizar el plan.");
    } finally {
      setBusy(false);
    }
  }

  async function updateActive(nextActive: boolean) {
    setBusy(true);
    setMessage(null);
    try {
      const response = await fetch(`/api/session/admin/users/${userId}/active`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ is_active: nextActive, note: "Cambio manual desde el panel web" }),
      });
      const payload = (await response.json()) as { detail?: string };
      if (!response.ok) throw new Error(payload.detail ?? "No fue posible cambiar el estado del usuario.");
      window.location.reload();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "No fue posible cambiar el estado del usuario.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="admin-actions">
      {currentPlan !== "pro" ? (
        <button className="button button-primary button-small" disabled={busy} onClick={() => updatePlan("pro")}>
          {requestedPlan === "pro" ? "Aprobar Pro" : "Dar Pro"}
        </button>
      ) : (
        <button className="button button-secondary button-small" disabled={busy} onClick={() => updatePlan("basic")}>
          Pasar a Basic
        </button>
      )}
      {!isSelf ? (
        <button className="button button-ghost button-small" disabled={busy} onClick={() => updateActive(!isActive)}>
          {isActive ? "Desactivar" : "Reactivar"}
        </button>
      ) : null}
      {message ? <small className="form-error">{message}</small> : null}
    </div>
  );
}
