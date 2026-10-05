"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

function extractMessage(payload: unknown): string {
  if (payload && typeof payload === "object" && "detail" in payload && typeof (payload as { detail?: unknown }).detail === "string") {
    return (payload as { detail: string }).detail;
  }
  return "No fue posible crear la cuenta.";
}

export function RegisterForm() {
  const router = useRouter();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");

    if (password.length < 10) {
      setError("La contraseña debe tener al menos 10 caracteres.");
      return;
    }
    if (password !== confirmPassword) {
      setError("Las contraseñas no coinciden.");
      return;
    }

    setLoading(true);
    try {
      const response = await fetch("/api/session/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, full_name: fullName.trim() || null }),
      });
      const payload = await response.json().catch(() => null);
      if (!response.ok) {
        setError(extractMessage(payload));
        return;
      }
      router.push("/onboarding");
      router.refresh();
    } catch {
      setError("No fue posible conectar con el servidor.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="auth-form" onSubmit={onSubmit} noValidate>
      <div className="field-group">
        <label htmlFor="full-name">Nombre completo</label>
        <input
          id="full-name"
          name="full_name"
          type="text"
          autoComplete="name"
          maxLength={120}
          value={fullName}
          onChange={(event) => setFullName(event.target.value)}
          placeholder="Tu nombre"
        />
      </div>

      <div className="field-group">
        <label htmlFor="email">Correo electrónico</label>
        <input
          id="email"
          name="email"
          type="email"
          autoComplete="email"
          required
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          placeholder="tu@correo.com"
        />
      </div>

      <div className="field-group">
        <label htmlFor="password">Contraseña</label>
        <input
          id="password"
          name="password"
          type="password"
          autoComplete="new-password"
          required
          minLength={10}
          maxLength={128}
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          placeholder="Mínimo 10 caracteres"
        />
      </div>

      <div className="field-group">
        <label htmlFor="confirm-password">Confirmar contraseña</label>
        <input
          id="confirm-password"
          name="confirm_password"
          type="password"
          autoComplete="new-password"
          required
          minLength={10}
          maxLength={128}
          value={confirmPassword}
          onChange={(event) => setConfirmPassword(event.target.value)}
          placeholder="Repite tu contraseña"
        />
      </div>

      {error ? <p className="form-error" role="alert">{error}</p> : null}

      <button className="button button-primary button-block" type="submit" disabled={loading}>
        {loading ? "Creando cuenta…" : "Crear cuenta"}
      </button>

      <p className="auth-switch">
        ¿Ya tienes cuenta? <Link href="/login">Iniciar sesión</Link>
      </p>
    </form>
  );
}
