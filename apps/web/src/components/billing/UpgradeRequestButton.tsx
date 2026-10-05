"use client";

import { useState } from "react";

interface UpgradeRequestButtonProps {
  alreadyRequested?: boolean;
}

export function UpgradeRequestButton({ alreadyRequested = false }: UpgradeRequestButtonProps) {
  const [requested, setRequested] = useState(alreadyRequested);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(alreadyRequested ? "Tu solicitud Pro ya está registrada." : "");

  async function requestUpgrade() {
    if (requested || loading) return;
    setLoading(true);
    setMessage("");
    try {
      const response = await fetch("/api/session/billing/request-upgrade", { method: "POST" });
      const payload = (await response.json().catch(() => null)) as { message?: string; detail?: string } | null;
      if (!response.ok) {
        setMessage(payload?.detail ?? "No fue posible registrar la solicitud.");
        return;
      }
      setRequested(true);
      setMessage(payload?.message ?? "Solicitud Pro registrada.");
    } catch {
      setMessage("No fue posible conectar con el servidor.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="upgrade-action">
      <button className="button button-primary" type="button" onClick={requestUpgrade} disabled={requested || loading}>
        {loading ? "Registrando…" : requested ? "Solicitud registrada" : "Me interesa Pro"}
      </button>
      {message ? <p className="muted upgrade-message" role="status">{message}</p> : null}
    </div>
  );
}
