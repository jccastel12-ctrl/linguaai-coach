"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useMemo, useState } from "react";
import type { CefrLevel, Language } from "@/types";

const LEVELS: Array<{ value: CefrLevel; label: string }> = [
  { value: "A1", label: "A1 · Principiante" },
  { value: "A2", label: "A2 · Básico" },
  { value: "B1", label: "B1 · Intermedio" },
  { value: "B2", label: "B2 · Intermedio alto" },
  { value: "C1", label: "C1 · Avanzado" },
  { value: "C2", label: "C2 · Dominio" },
];

function extractMessage(payload: unknown): string {
  if (payload && typeof payload === "object" && "detail" in payload && typeof (payload as { detail?: unknown }).detail === "string") {
    return (payload as { detail: string }).detail;
  }
  return "No fue posible guardar tu configuración.";
}

export function OnboardingForm({ languages }: { languages: Language[] }) {
  const router = useRouter();
  const initialNative = languages.find((language) => language.code === "es")?.code ?? languages[0]?.code ?? "es";
  const initialLearning = languages.find((language) => language.code === "en")?.code ?? languages[1]?.code ?? languages[0]?.code ?? "en";
  const [nativeLanguage, setNativeLanguage] = useState(initialNative);
  const [learningLanguage, setLearningLanguage] = useState(initialLearning);
  const [level, setLevel] = useState<CefrLevel>("A1");
  const [dailyGoal, setDailyGoal] = useState(15);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const availableLearningLanguages = useMemo(
    () => languages.filter((language) => language.code !== nativeLanguage),
    [languages, nativeLanguage],
  );

  function onNativeChange(code: string) {
    setNativeLanguage(code);
    if (learningLanguage === code) {
      const replacement = languages.find((language) => language.code !== code);
      if (replacement) setLearningLanguage(replacement.code);
    }
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await fetch("/api/session/onboarding", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          native_language_code: nativeLanguage,
          learning_language_code: learningLanguage,
          cefr_level: level,
          daily_goal_minutes: dailyGoal,
        }),
      });
      const payload = await response.json().catch(() => null);
      if (!response.ok) {
        setError(extractMessage(payload));
        return;
      }
      router.push("/dashboard");
      router.refresh();
    } catch {
      setError("No fue posible conectar con el servidor.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="auth-form" onSubmit={onSubmit}>
      <div className="field-group">
        <label htmlFor="native-language">Tu idioma nativo</label>
        <select id="native-language" value={nativeLanguage} onChange={(event) => onNativeChange(event.target.value)}>
          {languages.map((language) => (
            <option key={language.code} value={language.code}>{language.native_name}</option>
          ))}
        </select>
      </div>

      <div className="field-group">
        <label htmlFor="learning-language">Idioma que quieres aprender</label>
        <select id="learning-language" value={learningLanguage} onChange={(event) => setLearningLanguage(event.target.value)}>
          {availableLearningLanguages.map((language) => (
            <option key={language.code} value={language.code}>{language.native_name}</option>
          ))}
        </select>
      </div>

      <div className="field-group">
        <label htmlFor="level">Nivel actual</label>
        <select id="level" value={level} onChange={(event) => setLevel(event.target.value as CefrLevel)}>
          {LEVELS.map((item) => (
            <option key={item.value} value={item.value}>{item.label}</option>
          ))}
        </select>
      </div>

      <div className="field-group">
        <label htmlFor="daily-goal">Meta diaria</label>
        <select id="daily-goal" value={dailyGoal} onChange={(event) => setDailyGoal(Number(event.target.value))}>
          <option value={10}>10 minutos</option>
          <option value={15}>15 minutos</option>
          <option value={20}>20 minutos</option>
          <option value={30}>30 minutos</option>
          <option value={45}>45 minutos</option>
        </select>
      </div>

      {error ? <p className="form-error" role="alert">{error}</p> : null}

      <button className="button button-primary button-block" type="submit" disabled={loading || languages.length < 2}>
        {loading ? "Guardando…" : "Guardar y continuar"}
      </button>
    </form>
  );
}
