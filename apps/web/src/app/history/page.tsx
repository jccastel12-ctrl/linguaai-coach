import Link from "next/link";
import { redirect } from "next/navigation";
import { getCurrentUser } from "@/lib/server-auth";
import { getTutorSessions, getTutorStats } from "@/lib/tutor-server";

const languageNames: Record<string, string> = { es: "Español", en: "English", sr: "Srpski" };
const personalityNames: Record<string, string> = { friendly: "Amigable", patient: "Paciente", professional: "Profesional" };

function formatDate(value: string) {
  return new Intl.DateTimeFormat("es-CO", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

export default async function HistoryPage() {
  const user = await getCurrentUser();
  if (!user) redirect("/login");

  const [sessions, stats] = await Promise.all([getTutorSessions(50), getTutorStats()]);

  return (
    <section className="dashboard-shell">
      <div className="section-heading-row">
        <div>
          <span className="eyebrow">Historial</span>
          <h1 className="page-title">Tus conversaciones</h1>
          <p className="muted">Revisa prácticas anteriores, consulta correcciones y retoma una sesión cuando quieras.</p>
        </div>
        <div className="heading-actions">
          <Link className="button button-secondary button-small" href="/dashboard">Panel</Link>
          <Link className="button button-primary button-small" href="/tutor">Nueva práctica</Link>
        </div>
      </div>

      <div className="dashboard-grid compact-stats">
        <article className="dashboard-card">
          <span className="card-label">Sesiones</span><strong>{stats?.total_sessions ?? sessions.length}</strong><span className="muted">Conversaciones guardadas</span>
        </article>
        <article className="dashboard-card">
          <span className="card-label">Intervenciones</span><strong>{stats?.total_user_messages ?? 0}</strong><span className="muted">Mensajes tuyos al tutor</span>
        </article>
        <article className="dashboard-card">
          <span className="card-label">Últimos 7 días</span><strong>{stats?.sessions_last_7_days ?? 0}</strong><span className="muted">Sesiones iniciadas</span>
        </article>
      </div>

      {sessions.length === 0 ? (
        <div className="empty-state card">
          <h2>Aún no hay conversaciones</h2>
          <p className="muted">Tu primera sesión aparecerá aquí después de conversar con el tutor.</p>
          <Link className="button button-primary" href="/tutor">Empezar práctica</Link>
        </div>
      ) : (
        <div className="history-list">
          {sessions.map((session) => (
            <article className="history-item" key={session.id}>
              <div>
                <span className="card-label">{languageNames[session.target_language_code] ?? session.target_language_code} · {session.cefr_level}</span>
                <h2>{session.title || "Conversación sin título"}</h2>
                <p className="muted">{personalityNames[session.personality] ?? session.personality} · Actualizada {formatDate(session.updated_at)}</p>
              </div>
              <div className="history-actions">
                <Link className="button button-secondary button-small" href={`/history/${session.id}`}>Ver</Link>
                <Link className="button button-primary button-small" href={`/tutor?session=${session.id}`}>Continuar</Link>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
