import Link from "next/link";
import { redirect } from "next/navigation";
import { getCurrentUser } from "@/lib/server-auth";
import { getTutorMemory, getTutorStats } from "@/lib/tutor-server";
import { getPronunciationStats } from "@/lib/pronunciation-server";

const categoryNames: Record<string, string> = {
  grammar: "Gramática", vocabulary: "Vocabulario", pronunciation: "Pronunciación", usage: "Uso y expresión",
};

export default async function ProgressPage() {
  const user = await getCurrentUser();
  if (!user) redirect("/login");

  const [stats, memories, pronunciationStats] = await Promise.all([getTutorStats(), getTutorMemory(50), getPronunciationStats()]);
  const repeated = memories.filter((item) => item.occurrence_count > 1);

  return (
    <section className="dashboard-shell">
      <div className="section-heading-row">
        <div>
          <span className="eyebrow">Seguimiento</span>
          <h1 className="page-title">Tu progreso de práctica</h1>
          <p className="muted">Estas métricas describen tu actividad y los patrones detectados por el tutor; no sustituyen una evaluación formal de nivel.</p>
        </div>
        <div className="heading-actions">
          <Link className="button button-secondary button-small" href="/history">Historial</Link>
          <Link className="button button-primary button-small" href="/tutor">Practicar</Link>
        </div>
      </div>

      <div className="dashboard-grid">
        <article className="dashboard-card"><span className="card-label">Sesiones</span><strong>{stats?.total_sessions ?? 0}</strong><span className="muted">Prácticas guardadas</span></article>
        <article className="dashboard-card"><span className="card-label">Mensajes</span><strong>{stats?.total_user_messages ?? 0}</strong><span className="muted">Intervenciones al tutor</span></article>
        <article className="dashboard-card"><span className="card-label">Correcciones</span><strong>{stats?.total_corrections ?? 0}</strong><span className="muted">Respuestas con corrección registrada</span></article>
        <article className="dashboard-card"><span className="card-label">Patrones recurrentes</span><strong>{stats?.repeated_patterns ?? repeated.length}</strong><span className="muted">Aparecieron más de una vez</span></article>
        <article className="dashboard-card"><span className="card-label">Pronunciación</span><strong>{pronunciationStats?.average_score ?? "—"}%</strong><span className="muted">Promedio en {pronunciationStats?.total_attempts ?? 0} intentos de reconocimiento</span><Link className="button button-secondary button-small" href="/pronunciation">Practicar</Link></article>
      </div>

      <section className="progress-section">
        <div className="section-heading-row compact">
          <div><h2>Aspectos para reforzar</h2><p className="muted">Se ordenan por frecuencia de aparición en tus conversaciones.</p></div>
        </div>
        {memories.length === 0 ? (
          <div className="empty-state card"><h3>Sin patrones registrados todavía</h3><p className="muted">Cuando el tutor detecte una corrección, quedará disponible aquí.</p></div>
        ) : (
          <div className="memory-list">
            {memories.map((memory) => (
              <article className="memory-item" key={memory.id}>
                <div className="memory-count" aria-label={`${memory.occurrence_count} apariciones`}>{memory.occurrence_count}×</div>
                <div className="memory-content">
                  <div className="memory-meta"><span className="memory-category">{categoryNames[memory.category] ?? memory.category}</span><span>{memory.language_code.toUpperCase()}</span></div>
                  <h3>{memory.note}</h3>
                  {memory.last_example ? <p className="muted">Último ejemplo: “{memory.last_example}”</p> : null}
                </div>
              </article>
            ))}
          </div>
        )}
      </section>

      {stats?.most_frequent_pattern ? (
        <div className="notice-card">
          <div><strong>Foco sugerido para la próxima práctica</strong><p className="muted">Tu patrón más frecuente registrado es <code>{stats.most_frequent_pattern}</code>. El tutor puede ayudarte a practicarlo con ejemplos.</p></div>
          <Link className="button button-primary" href="/tutor">Practicar ahora</Link>
        </div>
      ) : null}
    </section>
  );
}
