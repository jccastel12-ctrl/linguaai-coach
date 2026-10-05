"use client";

import { useMemo, useState } from "react";
import { useBrowserSpeech } from "@/lib/use-browser-speech";
import type {
  CefrLevel,
  LanguageCode,
  PronunciationEvaluation,
  PronunciationExercise,
  PronunciationStats,
} from "@/types";

interface PronunciationPracticeProps {
  languageCode: LanguageCode;
  cefrLevel: CefrLevel;
  exercises: PronunciationExercise[];
  initialStats: PronunciationStats | null;
}

function scoreLabel(score: number): string {
  if (score >= 92) return "Excelente coincidencia";
  if (score >= 78) return "Buen intento";
  if (score >= 60) return "En progreso";
  return "Practica de nuevo";
}

function apiError(payload: unknown): string {
  if (payload && typeof payload === "object" && "detail" in payload && typeof (payload as { detail?: unknown }).detail === "string") {
    return (payload as { detail: string }).detail;
  }
  return "No fue posible evaluar la pronunciación.";
}

export function PronunciationPractice({
  languageCode,
  cefrLevel,
  exercises,
  initialStats,
}: PronunciationPracticeProps) {
  const [exerciseIndex, setExerciseIndex] = useState(0);
  const [recognizedText, setRecognizedText] = useState("");
  const [evaluation, setEvaluation] = useState<PronunciationEvaluation | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const speech = useBrowserSpeech();
  const exercise = exercises[exerciseIndex] ?? null;

  const canEvaluate = Boolean(exercise && recognizedText.trim() && !loading && !speech.listening);
  const statsSummary = useMemo(() => {
    if (!initialStats || initialStats.total_attempts === 0) return "Aún no hay intentos guardados";
    return `${initialStats.total_attempts} intentos · promedio ${initialStats.average_score ?? "—"}% · mejor ${initialStats.best_score ?? "—"}%`;
  }, [initialStats]);

  function selectExercise(index: number) {
    speech.stopListening();
    speech.stopSpeaking();
    setExerciseIndex(index);
    setRecognizedText("");
    setEvaluation(null);
    setError("");
  }

  function toggleRecording() {
    if (!exercise) return;
    if (speech.listening) {
      speech.stopListening();
      return;
    }
    speech.stopSpeaking();
    setRecognizedText("");
    setEvaluation(null);
    setError("");
    speech.startListening(languageCode, "", (text) => setRecognizedText(text));
  }

  async function evaluate() {
    if (!exercise || !canEvaluate) return;
    setLoading(true);
    setError("");
    try {
      const response = await fetch("/api/session/pronunciation/evaluate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          language_code: languageCode,
          cefr_level: cefrLevel,
          expected_text: exercise.text,
          recognized_text: recognizedText,
          focus_sound: exercise.focus_sound,
        }),
      });
      const payload = (await response.json().catch(() => null)) as PronunciationEvaluation | { detail?: string } | null;
      if (!response.ok || !payload || !("overall_score" in payload)) {
        setError(apiError(payload));
        return;
      }
      setEvaluation(payload);
    } catch {
      setError("No fue posible conectar con el evaluador.");
    } finally {
      setLoading(false);
    }
  }

  if (!exercise) {
    return <div className="card empty-state"><h2>No hay ejercicios disponibles</h2><p className="muted">Vuelve más tarde o cambia tu nivel.</p></div>;
  }

  return (
    <div className="pronunciation-layout">
      <aside className="card pronunciation-sidebar">
        <span className="card-label">Práctica</span>
        <strong>Nivel {cefrLevel}</strong>
        <p className="muted">{statsSummary}</p>
        <div className="pronunciation-exercise-list" aria-label="Frases de práctica">
          {exercises.map((item, index) => (
            <button
              key={item.id}
              type="button"
              className={index === exerciseIndex ? "is-active" : ""}
              onClick={() => selectExercise(index)}
            >
              <span>Frase {index + 1}</span>
              <small>{item.focus_sound ? `Foco: ${item.focus_sound}` : "Ritmo y claridad"}</small>
            </button>
          ))}
        </div>
        <p className="tutor-note muted">
          Esta versión evalúa la coincidencia entre la frase objetivo y lo que reconoce el navegador. Todavía no es un análisis acústico de fonemas.
        </p>
      </aside>

      <section className="pronunciation-card">
        <div className="pronunciation-target">
          <div>
            <span className="eyebrow">Escucha · repite · compara</span>
            <h2>{exercise.text}</h2>
            <p>{exercise.tip}</p>
          </div>
          <button
            className={`button button-secondary${speech.speaking ? " voice-button-active" : ""}`}
            type="button"
            onClick={() => {
              if (speech.speaking) speech.stopSpeaking();
              else speech.speak(exercise.text, languageCode);
            }}
            disabled={!speech.synthesisSupported}
          >
            {speech.speaking ? "■ Detener modelo" : "🔊 Escuchar modelo"}
          </button>
        </div>

        <div className="pronunciation-capture">
          <button
            type="button"
            className={`pronunciation-record-button${speech.listening ? " is-listening" : ""}`}
            onClick={toggleRecording}
            disabled={!speech.recognitionSupported || loading}
            aria-pressed={speech.listening}
          >
            <span aria-hidden="true">{speech.listening ? "■" : "🎙"}</span>
            {speech.listening ? "Detener" : "Pronunciar frase"}
          </button>
          <p className="muted">{speech.listening ? "Te estoy escuchando…" : "Pulsa el micrófono y repite la frase completa."}</p>
          {speech.speechMessage ? <p className="voice-status pronunciation-status" role="status">{speech.speechMessage}</p> : null}
        </div>

        <div className="pronunciation-heard">
          <span className="card-label">Lo que entendió el reconocimiento</span>
          <p>{recognizedText || "Tu transcripción aparecerá aquí."}</p>
        </div>

        {error ? <p className="form-error" role="alert">{error}</p> : null}

        <div className="pronunciation-actions">
          <button className="button button-primary" type="button" onClick={evaluate} disabled={!canEvaluate}>
            {loading ? "Evaluando…" : "Evaluar intento"}
          </button>
          <button className="button button-secondary" type="button" onClick={() => { setRecognizedText(""); setEvaluation(null); setError(""); }}>
            Limpiar
          </button>
        </div>

        {evaluation ? (
          <div className="pronunciation-result-card" aria-live="polite">
            <div className="pronunciation-score-ring" aria-label={`Puntuación ${evaluation.overall_score} de 100`}>
              <strong>{evaluation.overall_score}</strong><span>/100</span>
            </div>
            <div className="pronunciation-result-main">
              <span className="eyebrow">{scoreLabel(evaluation.overall_score)}</span>
              <h3>{evaluation.feedback}</h3>
              <div className="pronunciation-metrics">
                <div><span>Palabras</span><strong>{evaluation.word_accuracy}%</strong></div>
                <div><span>Similitud</span><strong>{evaluation.transcript_similarity}%</strong></div>
                <div><span>Foco</span><strong>{evaluation.focus_sound ?? "Claridad"}</strong></div>
              </div>
              {evaluation.missing_words.length ? (
                <p className="pronunciation-diff"><strong>Revisa:</strong> {evaluation.missing_words.join(", ")}</p>
              ) : null}
              {evaluation.extra_words.length ? (
                <p className="pronunciation-diff"><strong>Se reconoció además:</strong> {evaluation.extra_words.join(", ")}</p>
              ) : null}
            </div>
          </div>
        ) : null}
      </section>
    </div>
  );
}
