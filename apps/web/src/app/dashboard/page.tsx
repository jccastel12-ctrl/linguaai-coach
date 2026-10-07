import Link from "next/link";
import { redirect } from "next/navigation";
import { LogoutButton } from "@/components/dashboard/LogoutButton";
import { getBillingOverview } from "@/lib/billing-server";
import { getCurrentUser } from "@/lib/server-auth";
import { getTutorStats } from "@/lib/tutor-server";

const languageNames: Record<string, string> = {
  es: "Español",
  en: "English",
  sr: "Srpski",
  it: "Italiano",
};

export default async function DashboardPage() {
  const user = await getCurrentUser();
  if (!user) redirect("/login");
  const [tutorStats, billing] = await Promise.all([getTutorStats(), getBillingOverview()]);

  const primaryLanguage = user.languages.find((language) => language.is_primary) ?? user.languages[0];
  const needsOnboarding = !user.profile?.native_language_code || !primaryLanguage;

  return (
    <section className="dashboard-shell">
      <div className="dashboard-heading">
        <div>
          <span className="eyebrow">Panel del estudiante</span>
          <h1>Hola, {user.profile?.display_name || user.full_name || user.email}</h1>
          <p className="muted">Tu espacio para aprender, practicar y medir tu progreso.</p>
        </div>
        <LogoutButton />
      </div>

      {needsOnboarding ? (
        <div className="notice-card">
          <div>
            <strong>Completa tu configuración inicial</strong>
            <p className="muted">Necesitamos tu idioma nativo, idioma objetivo y nivel para personalizar la experiencia.</p>
          </div>
          <Link className="button button-primary" href="/onboarding">Configurar ahora</Link>
        </div>
      ) : null}

      <div className="dashboard-grid">
        <article className="dashboard-card">
          <span className="card-label">Idioma de aprendizaje</span>
          <strong>{primaryLanguage ? languageNames[primaryLanguage.language_code] ?? primaryLanguage.language_code : "Sin configurar"}</strong>
          <span className="muted">Nivel {primaryLanguage?.cefr_level ?? "—"}</span>
        </article>
        <article className="dashboard-card">
          <span className="card-label">Meta diaria</span>
          <strong>{user.profile?.daily_goal_minutes ?? 15} min</strong>
          <span className="muted">Práctica recomendada</span>
        </article>
        <article className="dashboard-card">
          <span className="card-label">Tutor IA</span>
          <strong>Disponible</strong>
          <span className="muted">Conversación escrita, correcciones y memoria de errores</span>
          {!needsOnboarding ? <Link className="button button-primary button-small" href="/tutor">Practicar ahora</Link> : null}
        </article>
        <article className="dashboard-card">
          <span className="card-label">Traductor</span>
          <strong>ES · EN · SR</strong>
          <span className="muted">Traducción de texto con arquitectura preparada para voz</span>
          {!needsOnboarding ? <Link className="button button-secondary button-small" href="/translator">Abrir traductor</Link> : null}
        </article>
        <article className="dashboard-card">
          <span className="card-label">Pronunciación</span>
          <strong>Escucha y repite</strong>
          <span className="muted">Compara la frase objetivo con lo que reconoce tu navegador</span>
          {!needsOnboarding ? <Link className="button button-secondary button-small" href="/pronunciation">Practicar voz</Link> : null}
        </article>
        <article className="dashboard-card">
          <span className="card-label">Historial</span>
          <strong>{tutorStats?.total_sessions ?? 0} sesiones</strong>
          <span className="muted">{tutorStats?.total_user_messages ?? 0} intervenciones guardadas</span>
          {!needsOnboarding ? <Link className="button button-secondary button-small" href="/history">Ver conversaciones</Link> : null}
        </article>
        <article className="dashboard-card">
          <span className="card-label">Seguimiento</span>
          <strong>{tutorStats?.repeated_patterns ?? 0} recurrentes</strong>
          <span className="muted">Patrones que aparecieron más de una vez</span>
          {!needsOnboarding ? <Link className="button button-secondary button-small" href="/progress">Ver progreso</Link> : null}
        </article>
        <article className="dashboard-card">
          <span className="card-label">Plan</span>
          <strong>{billing?.plan.name ?? "Basic"}</strong>
          <span className="muted">{billing?.requested_plan === "pro" ? "Solicitud Pro registrada" : "Consulta tus límites diarios"}</span>
          <Link className="button button-secondary button-small" href="/plans">Ver plan y uso</Link>
        </article>
        {user.is_superuser ? (
          <article className="dashboard-card dashboard-card-admin">
            <span className="card-label">Administración</span>
            <strong>Usuarios y planes</strong>
            <span className="muted">Revisa solicitudes Pro, accesos y métricas operativas.</span>
            <Link className="button button-secondary button-small" href="/admin">Abrir administración</Link>
          </article>
        ) : null}
      </div>

      <section className="next-step-card">
        <div>
          <span className="eyebrow">Tu siguiente paso</span>
          <h2>Empieza una práctica guiada</h2>
          <p className="muted">El tutor de texto adapta la conversación a tu idioma, nivel y estilo elegido, y conserva patrones de error para futuras sesiones.</p>
          {!needsOnboarding ? <Link className="button button-secondary" href="/tutor">Abrir Tutor IA</Link> : null}
        </div>
      </section>
    </section>
  );
}
