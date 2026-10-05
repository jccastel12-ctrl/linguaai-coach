import Link from "next/link";
import { redirect } from "next/navigation";
import { TranslatorPanel } from "@/components/translator/TranslatorPanel";
import { getCurrentUser } from "@/lib/server-auth";
import type { LanguageCode } from "@/types";

function supported(code: string | null | undefined): code is LanguageCode {
  return code === "es" || code === "en" || code === "sr";
}

export default async function TranslatorPage() {
  const user = await getCurrentUser();
  if (!user) redirect("/login");

  const primaryLanguage = user.languages.find((language) => language.is_primary) ?? user.languages[0];
  const native = supported(user.profile?.native_language_code) ? user.profile.native_language_code : "es";
  const learning = supported(primaryLanguage?.language_code) ? primaryLanguage.language_code : native === "en" ? "es" : "en";
  const source = native;
  const target = learning === source ? (source === "en" ? "es" : "en") : learning;

  return (
    <section className="translator-shell">
      <div className="section-heading-row">
        <div>
          <span className="eyebrow">Traductor · español · inglés · serbio</span>
          <h1 className="page-title">Traduce y aprende en el mismo lugar</h1>
          <p className="muted">
            Escribe o dicta una frase, tradúcela y escucha el resultado con la voz disponible en tu dispositivo.
          </p>
        </div>
        <div className="heading-actions">
          <Link className="button button-secondary button-small" href="/tutor">Abrir Tutor</Link>
          <Link className="button button-secondary button-small" href="/dashboard">Panel</Link>
        </div>
      </div>

      <TranslatorPanel initialSourceLanguage={source} initialTargetLanguage={target} />

      <div className="notice-card translator-roadmap-note">
        <div>
          <strong>Voz básica activada</strong>
          <p className="muted">El dictado y la lectura en voz alta usan las capacidades nativas del navegador, sin consumo obligatorio de una API externa. La evaluación fonética avanzada se añadirá después.</p>
        </div>
      </div>
    </section>
  );
}
