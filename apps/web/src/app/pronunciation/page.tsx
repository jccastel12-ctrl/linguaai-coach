import Link from "next/link";
import { redirect } from "next/navigation";
import { PronunciationPractice } from "@/components/pronunciation/PronunciationPractice";
import { getPronunciationExercises, getPronunciationStats } from "@/lib/pronunciation-server";
import { getCurrentUser } from "@/lib/server-auth";
import type { LanguageCode } from "@/types";

const languageNames: Record<string, string> = { es: "Español", en: "English", sr: "Srpski" };

export default async function PronunciationPage() {
  const user = await getCurrentUser();
  if (!user) redirect("/login");
  const primaryLanguage = user.languages.find((language) => language.is_primary) ?? user.languages[0];
  if (!user.profile?.native_language_code || !primaryLanguage) redirect("/onboarding");

  const languageCode = primaryLanguage.language_code as LanguageCode;
  const [exercises, stats] = await Promise.all([
    getPronunciationExercises(languageCode, primaryLanguage.cefr_level),
    getPronunciationStats(),
  ]);

  return (
    <section className="pronunciation-shell">
      <div className="section-heading-row">
        <div>
          <span className="eyebrow">Pronunciación · MVP de reconocimiento</span>
          <h1 className="page-title">Practica {languageNames[languageCode] ?? languageCode} en voz alta</h1>
          <p className="muted">Escucha una referencia, repite la frase y compara qué entendió el reconocimiento de voz.</p>
        </div>
        <div className="heading-actions">
          <Link className="button button-secondary button-small" href="/tutor">Tutor</Link>
          <Link className="button button-secondary button-small" href="/progress">Progreso</Link>
        </div>
      </div>
      <PronunciationPractice
        languageCode={languageCode}
        cefrLevel={primaryLanguage.cefr_level}
        exercises={exercises}
        initialStats={stats}
      />
    </section>
  );
}
