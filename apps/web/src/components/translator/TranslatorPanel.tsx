"use client";

import { FormEvent, useMemo, useState } from "react";
import { useBrowserSpeech } from "@/lib/use-browser-speech";
import type { LanguageCode, TranslationResponse } from "@/types";

const languageLabels: Record<LanguageCode, string> = {
  es: "Español",
  en: "English",
  sr: "Srpski",
};

const demoExamples: Record<LanguageCode, string[]> = {
  es: ["Necesito ayuda", "¿Dónde está el aeropuerto?", "Me llamo Ana"],
  en: ["Thank you", "Can you repeat?", "My name is Mark"],
  sr: ["Zdravo", "Ne razumem", "Zovem se Mila"],
};

function extractMessage(payload: unknown): string {
  if (payload && typeof payload === "object" && "detail" in payload && typeof (payload as { detail?: unknown }).detail === "string") {
    return (payload as { detail: string }).detail;
  }
  return "No fue posible traducir el texto.";
}

interface TranslatorPanelProps {
  initialSourceLanguage: LanguageCode;
  initialTargetLanguage: LanguageCode;
}

export function TranslatorPanel({ initialSourceLanguage, initialTargetLanguage }: TranslatorPanelProps) {
  const [sourceLanguage, setSourceLanguage] = useState<LanguageCode>(initialSourceLanguage);
  const [targetLanguage, setTargetLanguage] = useState<LanguageCode>(initialTargetLanguage);
  const [text, setText] = useState("");
  const [result, setResult] = useState<TranslationResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const speech = useBrowserSpeech();

  const canTranslate = useMemo(
    () => text.trim().length > 0 && sourceLanguage !== targetLanguage && !loading,
    [text, sourceLanguage, targetLanguage, loading],
  );

  function resetResult() {
    setResult(null);
    setError("");
    setCopied(false);
    speech.clearSpeechMessage();
  }

  function swapLanguages() {
    speech.stopListening();
    speech.stopSpeaking();
    setSourceLanguage(targetLanguage);
    setTargetLanguage(sourceLanguage);
    if (result) setText(result.translated_text);
    resetResult();
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canTranslate) return;
    setLoading(true);
    setError("");
    setCopied(false);
    speech.stopSpeaking();

    try {
      const response = await fetch("/api/session/translate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: text.trim(),
          source_language: sourceLanguage,
          target_language: targetLanguage,
        }),
      });
      const payload = (await response.json().catch(() => null)) as TranslationResponse | { detail?: string } | null;
      if (!response.ok || !payload || !("translated_text" in payload)) {
        setResult(null);
        setError(extractMessage(payload));
        return;
      }
      setResult(payload);
    } catch {
      setResult(null);
      setError("No fue posible conectar con el servidor.");
    } finally {
      setLoading(false);
    }
  }

  async function copyTranslation() {
    if (!result) return;
    try {
      await navigator.clipboard.writeText(result.translated_text);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1600);
    } catch {
      setCopied(false);
    }
  }

  function toggleDictation() {
    if (speech.listening) {
      speech.stopListening();
      return;
    }
    speech.startListening(sourceLanguage, text, (nextText) => {
      setText(nextText.slice(0, 5000));
      setResult(null);
      setError("");
    });
  }

  function togglePlayback() {
    if (!result) return;
    if (speech.speaking) speech.stopSpeaking();
    else speech.speak(result.translated_text, targetLanguage);
  }

  return (
    <div className="translator-card">
      <div className="translator-language-row">
        <div className="field-group translator-language-field">
          <label htmlFor="source-language">Desde</label>
          <select
            id="source-language"
            value={sourceLanguage}
            onChange={(event) => {
              speech.stopListening();
              const next = event.target.value as LanguageCode;
              setSourceLanguage(next);
              if (next === targetLanguage) {
                const replacement = (["es", "en", "sr"] as LanguageCode[]).find((code) => code !== next) ?? "en";
                setTargetLanguage(replacement);
              }
              resetResult();
            }}
          >
            {Object.entries(languageLabels).map(([code, label]) => (
              <option key={code} value={code}>{label}</option>
            ))}
          </select>
        </div>

        <button className="swap-button" type="button" onClick={swapLanguages} aria-label="Intercambiar idiomas">
          ⇄
        </button>

        <div className="field-group translator-language-field">
          <label htmlFor="target-language">Hacia</label>
          <select
            id="target-language"
            value={targetLanguage}
            onChange={(event) => {
              speech.stopSpeaking();
              const next = event.target.value as LanguageCode;
              setTargetLanguage(next);
              if (next === sourceLanguage) {
                const replacement = (["es", "en", "sr"] as LanguageCode[]).find((code) => code !== next) ?? "es";
                setSourceLanguage(replacement);
              }
              resetResult();
            }}
          >
            {Object.entries(languageLabels).map(([code, label]) => (
              <option key={code} value={code}>{label}</option>
            ))}
          </select>
        </div>
      </div>

      <form className="translator-grid" onSubmit={submit}>
        <section className="translator-pane">
          <div className="translator-pane-heading">
            <span className="card-label">Texto original</span>
            <div className="voice-inline-actions">
              <span className="muted">{text.length}/5000</span>
              <button
                className={`voice-button${speech.listening ? " voice-button-active" : ""}`}
                type="button"
                onClick={toggleDictation}
                disabled={!speech.recognitionSupported || loading}
                aria-pressed={speech.listening}
                title={speech.recognitionSupported ? "Dictar con el micrófono" : "Dictado no disponible en este navegador"}
              >
                {speech.listening ? "■ Detener" : "🎙 Dictar"}
              </button>
            </div>
          </div>
          <label className="sr-only" htmlFor="translation-source">Texto para traducir</label>
          <textarea
            id="translation-source"
            value={text}
            onChange={(event) => {
              setText(event.target.value);
              resetResult();
            }}
            maxLength={5000}
            rows={10}
            placeholder={speech.listening ? "Escuchando… habla ahora" : "Escribe, pega o dicta un texto…"}
          />
          <div className="translator-examples">
            <span className="muted">Prueba:</span>
            {demoExamples[sourceLanguage].map((example) => (
              <button key={example} type="button" onClick={() => setText(example)}>{example}</button>
            ))}
          </div>
        </section>

        <section className="translator-pane translator-result-pane" aria-live="polite">
          <div className="translator-pane-heading">
            <span className="card-label">Traducción</span>
            {result ? (
              <div className="voice-inline-actions">
                <button className="text-button" type="button" onClick={copyTranslation}>
                  {copied ? "Copiado" : "Copiar"}
                </button>
                <button
                  className={`voice-button${speech.speaking ? " voice-button-active" : ""}`}
                  type="button"
                  onClick={togglePlayback}
                  disabled={!speech.synthesisSupported}
                  aria-pressed={speech.speaking}
                  title={speech.synthesisSupported ? "Escuchar traducción" : "Lectura en voz alta no disponible"}
                >
                  {speech.speaking ? "■ Detener" : "🔊 Escuchar"}
                </button>
              </div>
            ) : null}
          </div>
          <div className="translator-result">
            {loading ? <p className="muted">Traduciendo…</p> : null}
            {!loading && result ? <p>{result.translated_text}</p> : null}
            {!loading && !result ? <p className="muted">La traducción aparecerá aquí.</p> : null}
          </div>
          {result?.learning_note ? <p className="translator-note">{result.learning_note}</p> : null}
          {result?.provider === "rule_based" ? (
            <p className="translator-provider-note muted">
              Modo local de demostración. Las frases libres se habilitan al conectar el proveedor de IA.
            </p>
          ) : null}
        </section>

        {speech.speechMessage ? <p className="voice-status" role="status">{speech.speechMessage}</p> : null}
        {error ? <p className="form-error translator-error" role="alert">{error}</p> : null}
        <div className="translator-actions">
          <button className="button button-primary" type="submit" disabled={!canTranslate}>
            {loading ? "Traduciendo…" : "Traducir"}
          </button>
          <button
            className="button button-secondary"
            type="button"
            onClick={() => {
              speech.stopListening();
              speech.stopSpeaking();
              setText("");
              setResult(null);
              setError("");
            }}
            disabled={loading || (!text && !result)}
          >
            Limpiar
          </button>
        </div>
      </form>
    </div>
  );
}
