"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

function extractMessage(payload: unknown): string {
  if (payload && typeof payload === "object" && "detail" in payload && typeof (payload as { detail?: unknown }).detail === "string") {
    return (payload as { detail: string }).detail;
  }
  return "No fue posible iniciar sesión.";
}

export function LoginForm() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await fetch("/api/session/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const payload = await response.json().catch(() => null);
      if (!response.ok) {
        setError(extractMessage(payload));
        return;
      }
      router.push("/dashboard");
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
          autoComplete="current-password"
          required
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          placeholder="Tu contraseña"
        />
      </div>

      {error ? <p className="form-error" role="alert">{error}</p> : null}

      <button className="button button-primary button-block" type="submit" disabled={loading}>
        {loading ? "Ingresando…" : "Iniciar sesión"}
      </button>

      <p className="auth-switch"><Link href="/forgot-password">¿Olvidaste tu contraseña?</Link></p>
      <p className="auth-switch">
        ¿Aún no tienes cuenta? <Link href="/register">Crear cuenta</Link>
      </p>
    </form>
  );
}
