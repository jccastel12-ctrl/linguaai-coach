import Link from "next/link";
import { redirect } from "next/navigation";
import { TutorChat } from "@/components/tutor/TutorChat";
import { getCurrentUser } from "@/lib/server-auth";
import { getTutorSession } from "@/lib/tutor-server";

const languageNames: Record<string, string> = {
  es: "Español",
  en: "English",
  sr: "Srpski",
  it: "Italiano",
};

export default async function TutorPage({
  searchParams,
}: {
  searchParams: Promise<{ session?: string | string[] }>;
}) {
  const user = await getCurrentUser();
  if (!user) redirect("/login");

  const primaryLanguage = user.languages.find((language) => language.is_primary) ?? user.languages[0];
  if (!user.profile?.native_language_code || !primaryLanguage) redirect("/onboarding");

  const query = await searchParams;
  const requestedId = typeof query.session === "string" ? query.session : null;
  const previousSession = requestedId ? await getTutorSession(requestedId) : null;
  const targetLanguageCode = previousSession?.target_language_code ?? primaryLanguage.language_code;
  const cefrLevel = previousSession?.cefr_level ?? primaryLanguage.cefr_level;

  return (
    <section className="tutor-shell">
      <div className="tutor-page-heading section-heading-row">
        <div>
          <span className="eyebrow">Tutor IA · texto + voz + avatar</span>
          <h1>{previousSession ? "Continúa tu conversación" : `Practica ${languageNames[targetLanguageCode] ?? targetLanguageCode}`}</h1>
          <p className="muted">
            Conversa por texto o voz con un tutor visual que reacciona en tiempo real y conserva tus patrones de aprendizaje.
          </p>
        </div>
        <div className="heading-actions">
          <Link className="button button-secondary button-small" href="/history">Historial</Link>
          <Link className="button button-secondary button-small" href="/progress">Progreso</Link>
        </div>
      </div>

      <TutorChat
        targetLanguageCode={targetLanguageCode}
        cefrLevel={cefrLevel}
        learnerName={user.profile.display_name || user.full_name || "Estudiante"}
        initialSessionId={previousSession?.id ?? null}
        initialPersonality={previousSession?.personality ?? "patient"}
        initialMessages={previousSession?.turns ?? []}
      />
    </section>
  );
}
