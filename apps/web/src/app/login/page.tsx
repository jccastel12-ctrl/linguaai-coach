import { redirect } from "next/navigation";
import { LoginForm } from "@/components/auth/LoginForm";
import { getCurrentUser } from "@/lib/server-auth";

export default async function LoginPage() {
  if (await getCurrentUser()) redirect("/dashboard");

  return (
    <section className="auth-shell">
      <div className="auth-card">
        <span className="eyebrow">Bienvenido de nuevo</span>
        <h1>Continúa tu aprendizaje</h1>
        <p className="muted">Accede a tu perfil, progreso y práctica de idiomas.</p>
        <LoginForm />
      </div>
    </section>
  );
}
