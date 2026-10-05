import Link from "next/link";
import { notFound, redirect } from "next/navigation";
import { getCurrentUser } from "@/lib/server-auth";
import { getTutorSession } from "@/lib/tutor-server";

function formatDate(value: string) {
  return new Intl.DateTimeFormat("es-CO", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

export default async function HistoryDetailPage({ params }: { params: Promise<{ sessionId: string }> }) {
  const user = await getCurrentUser();
  if (!user) redirect("/login");

  const { sessionId } = await params;
  const session = await getTutorSession(sessionId);
  if (!session) notFound();

  return (
    <section className="dashboard-shell">
      <div className="section-heading-row">
        <div>
          <span className="eyebrow">Conversación guardada</span>
          <h1 className="page-title">{session.title || "Práctica con tutor"}</h1>
          <p className="muted">Nivel {session.cefr_level} · {formatDate(session.created_at)}</p>
        </div>
        <div className="heading-actions">
          <Link className="button button-secondary button-small" href="/history">Volver</Link>
          <Link className="button button-primary button-small" href={`/tutor?session=${session.id}`}>Continuar conversación</Link>
        </div>
      </div>

      <div className="transcript-card">
        {session.turns.length === 0 ? <p className="muted">Esta sesión todavía no tiene mensajes.</p> : null}
        {session.turns.map((turn) => (
          <article key={turn.id} className={`chat-message chat-message-${turn.role}`}>
            <div className="message-bubble">
              <span className="message-role">{turn.role === "user" ? "Tú" : "Tutor"}</span>
              <p>{turn.content}</p>
            </div>
            {turn.role === "assistant" && (turn.corrected_text || turn.explanation || turn.translation) ? (
              <div className="feedback-card">
                {turn.corrected_text ? <div><span>Corrección</span><strong>{turn.corrected_text}</strong></div> : null}
                {turn.explanation ? <div><span>Explicación</span><p>{turn.explanation}</p></div> : null}
                {turn.translation ? <div><span>Apoyo</span><p>{turn.translation}</p></div> : null}
              </div>
            ) : null}
          </article>
        ))}
      </div>
    </section>
  );
}
