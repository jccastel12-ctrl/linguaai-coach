import Link from "next/link";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { api } from "@/lib/api";
import type { HealthResponse, Language } from "@/types";

export const dynamic = "force-dynamic";

async function loadStatus(): Promise<{ health: HealthResponse | null; languages: Language[] }> {
  try {
    const [health, languages] = await Promise.all([api.health(), api.languages()]);
    return { health, languages };
  } catch {
    return { health: null, languages: [] };
  }
}

export default async function HomePage() {
  const { health, languages } = await loadStatus();

  return (
    <>
      <section className="hero hero-product">
        <span className="eyebrow">Aprendizaje de idiomas con IA</span>
        <h1>Aprende hablando. Practica con propósito.</h1>
        <p>
          LinguaAI Coach combina aprendizaje personalizado, práctica conversacional y una base preparada para tutoría con IA en español, inglés y serbio.
        </p>
        <div className="hero-actions">
          <Link className="button button-primary" href="/register">Comenzar con Basic</Link>
          <Link className="button button-secondary" href="/plans">Ver planes</Link>
          <Link className="button button-secondary" href="/login">Ya tengo una cuenta</Link>
        </div>
      </section>

      <div className="feature-grid">
        <Card title="Tu ruta personalizada">
          <p className="muted">Selecciona idioma, nivel MCER y una meta diaria para adaptar tu experiencia.</p>
        </Card>
        <Card title="Tutor IA de texto">
          <p className="muted">Practica conversaciones, recibe correcciones y registra patrones de error para personalizar el aprendizaje.</p>
        </Card>
        <Card title="Progreso conectado">
          <p className="muted">Cuenta, perfil e idioma de aprendizaje quedan asociados a un usuario autenticado.</p>
        </Card>
      </div>

      <div className="status-grid">
        <Card title="Estado del servicio">
          {health ? (
            <p><Badge tone="success">Conectada</Badge> API {health.service} v{health.version}</p>
          ) : (
            <p><Badge tone="danger">Sin conexión</Badge> Inicia API y base de datos para habilitar registro y acceso.</p>
          )}
        </Card>

        <Card title="Idiomas disponibles">
          {languages.length > 0 ? (
            <ul className="language-list">
              {languages.map((language) => (
                <li key={language.code}><strong>{language.native_name}</strong> <span className="muted">({language.code})</span></li>
              ))}
            </ul>
          ) : (
            <p className="muted">El catálogo se carga desde la API una vez aplicadas las migraciones.</p>
          )}
        </Card>
      </div>
    </>
  );
}
