import Link from "next/link";

export default function OfflinePage() {
  return (
    <section className="auth-shell">
      <div className="auth-card offline-card">
        <span className="eyebrow">Sin conexión</span>
        <h1>LinguaAI necesita Internet para esta función</h1>
        <p className="muted">
          La aplicación está instalada correctamente, pero el Tutor IA, el traductor y la sincronización de tu progreso requieren conexión.
        </p>
        <Link className="button button-primary button-block" href="/dashboard">Intentar de nuevo</Link>
      </div>
    </section>
  );
}
