import { redirect } from "next/navigation";
import type { Language } from "@/types";
import { OnboardingForm } from "@/components/onboarding/OnboardingForm";
import { backendFetch, getCurrentUser } from "@/lib/server-auth";

async function loadLanguages(): Promise<Language[]> {
  try {
    const response = await backendFetch("/api/v1/languages");
    if (!response.ok) return [];
    return (await response.json()) as Language[];
  } catch {
    return [];
  }
}

export default async function OnboardingPage() {
  const user = await getCurrentUser();
  if (!user) redirect("/login");

  const languages = await loadLanguages();

  return (
    <section className="auth-shell">
      <div className="auth-card auth-card-wide">
        <span className="eyebrow">Configuración inicial</span>
        <h1>Personaliza tu ruta de aprendizaje</h1>
        <p className="muted">Selecciona tu idioma, el idioma que quieres aprender y el nivel desde el que deseas empezar.</p>
        {languages.length >= 2 ? (
          <OnboardingForm languages={languages} />
        ) : (
          <p className="form-error">No fue posible cargar el catálogo de idiomas. Verifica que la API y las migraciones estén activas.</p>
        )}
      </div>
    </section>
  );
}
