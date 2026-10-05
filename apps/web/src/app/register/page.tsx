import { redirect } from "next/navigation";
import { RegisterForm } from "@/components/auth/RegisterForm";
import { getCurrentUser } from "@/lib/server-auth";

export default async function RegisterPage() {
  if (await getCurrentUser()) redirect("/dashboard");

  return (
    <section className="auth-shell">
      <div className="auth-card">
        <span className="eyebrow">Empieza gratis</span>
        <h1>Crea tu cuenta</h1>
        <p className="muted">Configura tu idioma y nivel después del registro.</p>
        <RegisterForm />
      </div>
    </section>
  );
}
