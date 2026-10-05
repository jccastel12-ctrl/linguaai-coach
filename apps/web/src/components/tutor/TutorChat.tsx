"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { useBrowserSpeech } from "@/lib/use-browser-speech";
import type { CefrLevel, TutorExchange, TutorPersonality, TutorTurn } from "@/types";
import {
  getTutorAvatarProfile,
  TutorAvatar,
  tutorAvatarProfiles,
  type TutorAvatarProfileId,
  type TutorAvatarState,
} from "@/components/tutor/TutorAvatar";

interface TutorChatProps {
  targetLanguageCode: string;
  cefrLevel: CefrLevel;
  learnerName: string;
  initialSessionId?: string | null;
  initialPersonality?: TutorPersonality;
  initialMessages?: TutorTurn[];
}

const personalityLabels: Record<TutorPersonality, string> = {
  friendly: "Amigable",
  patient: "Paciente",
  professional: "Profesional",
};

function extractMessage(payload: unknown): string {
  if (payload && typeof payload === "object" && "detail" in payload && typeof (payload as { detail?: unknown }).detail === "string") {
    return (payload as { detail: string }).detail;
  }
  return "No fue posible obtener respuesta del tutor.";
}

function previewPhrase(languageCode: string, name: string): string {
  if (languageCode === "es") return `Hola, soy ${name}. Practiquemos juntos.`;
  if (languageCode === "sr") return `Zdravo, ja sam ${name}. Hajde da vežbamo zajedno.`;
  return `Hello, I'm ${name}. Let's practice together.`;
}

export function TutorChat({
  targetLanguageCode,
  cefrLevel,
  learnerName,
  initialSessionId = null,
  initialPersonality = "patient",
  initialMessages = [],
}: TutorChatProps) {
  const [sessionId, setSessionId] = useState<string | null>(initialSessionId);
  const [personality, setPersonality] = useState<TutorPersonality>(initialPersonality);
  const [avatarId, setAvatarId] = useState<TutorAvatarProfileId>("lia");
  const [messages, setMessages] = useState<TutorTurn[]>(initialMessages);
  const [draft, setDraft] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const speech = useBrowserSpeech();

  useEffect(() => {
    const stored = window.localStorage.getItem("linguaai:tutor-avatar");
    if (stored === "lia" || stored === "alex" || stored === "mila") setAvatarId(stored);
  }, []);

  const avatarProfile = useMemo(() => getTutorAvatarProfile(avatarId), [avatarId]);
  const avatarState: TutorAvatarState = speech.listening
    ? "listening"
    : speech.speaking
      ? "speaking"
      : loading
        ? "thinking"
        : "idle";

  const canSend = useMemo(() => draft.trim().length > 0 && !loading, [draft, loading]);
  const starterPrompts = useMemo(() => {
    if (targetLanguageCode === "es") return ["Hola, me llamo Juan y yo sabo cocinar", "Háblame de tu ciudad"];
    if (targetLanguageCode === "sr") return ["Zdravo, ja sam 30 godina", "Reci mi nešto o svom gradu"];
    return ["Hello, my name is Juan and I have 30 years old", "Tell me about your city"];
  }, [targetLanguageCode]);
  const latestAssistantId = useMemo(
    () => [...messages].reverse().find((message) => message.role === "assistant")?.id ?? null,
    [messages],
  );

  function selectAvatar(nextId: TutorAvatarProfileId) {
    setAvatarId(nextId);
    window.localStorage.setItem("linguaai:tutor-avatar", nextId);
    speech.stopSpeaking();
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canSend) return;

    speech.stopListening();
    speech.stopSpeaking();
    const text = draft.trim();
    setDraft("");
    setError("");
    setLoading(true);

    try {
      const response = await fetch("/api/session/tutor/message", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          target_language_code: targetLanguageCode,
          cefr_level: cefrLevel,
          personality,
          message: text,
        }),
      });
      const payload = (await response.json().catch(() => null)) as TutorExchange | { detail?: string } | null;
      if (!response.ok || !payload || !("assistant_turn" in payload)) {
        setError(extractMessage(payload));
        setDraft(text);
        return;
      }
      setSessionId(payload.session_id);
      setMessages((current) => [...current, payload.user_turn, payload.assistant_turn]);
    } catch {
      setError("No fue posible conectar con el servidor.");
      setDraft(text);
    } finally {
      setLoading(false);
    }
  }

  function newConversation() {
    speech.stopListening();
    speech.stopSpeaking();
    setSessionId(null);
    setMessages([]);
    setDraft("");
    setError("");
  }

  function toggleDictation() {
    if (speech.listening) {
      speech.stopListening();
      return;
    }
    speech.startListening(targetLanguageCode, draft, (nextText) => {
      setDraft(nextText.slice(0, 2000));
      setError("");
    });
  }

  function speakAsTutor(text: string) {
    speech.speak(text, targetLanguageCode, {
      rate: avatarProfile.voiceRate,
      pitch: avatarProfile.voicePitch,
    });
  }

  return (
    <div className="tutor-layout">
      <aside className="tutor-settings card">
        <span className="card-label">Tutor virtual</span>
        <TutorAvatar profile={avatarProfile} state={avatarState} compact />

        <div className="avatar-profile-picker" role="group" aria-label="Elegir avatar del tutor">
          {tutorAvatarProfiles.map((profile) => (
            <button
              key={profile.id}
              type="button"
              className={profile.id === avatarId ? "is-active" : ""}
              onClick={() => selectAvatar(profile.id)}
              aria-pressed={profile.id === avatarId}
            >
              <strong>{profile.name}</strong>
              <span>{profile.description}</span>
            </button>
          ))}
        </div>

        <button
          className="button button-secondary button-block"
          type="button"
          onClick={() => (speech.speaking ? speech.stopSpeaking() : speakAsTutor(previewPhrase(targetLanguageCode, avatarProfile.name)))}
          disabled={!speech.synthesisSupported}
        >
          {speech.speaking ? "■ Detener voz" : "🔊 Probar voz"}
        </button>

        <div className="avatar-session-meta">
          <strong>{learnerName}</strong>
          <span>Nivel {cefrLevel}</span>
        </div>

        <div className="field-group">
          <label htmlFor="tutor-personality">Estilo pedagógico</label>
          <select
            id="tutor-personality"
            value={personality}
            onChange={(event) => setPersonality(event.target.value as TutorPersonality)}
            disabled={Boolean(sessionId)}
          >
            {Object.entries(personalityLabels).map(([value, label]) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
        </div>

        <button className="button button-secondary button-block" type="button" onClick={newConversation}>
          Nueva conversación
        </button>
        <p className="tutor-note muted">
          El avatar es ligero y funciona sin servicios externos. Reacciona al micrófono, al procesamiento y a la voz del tutor. La evaluación de pronunciación está disponible en su módulo dedicado.
        </p>
      </aside>

      <section className="chat-card">
        <div className="avatar-presence-bar" aria-live="polite">
          <TutorAvatar profile={avatarProfile} state={avatarState} compact showLabel={false} />
          <div>
            <strong>{avatarProfile.name}</strong>
            <span>
              {avatarState === "listening" ? "Te estoy escuchando" : avatarState === "thinking" ? "Estoy preparando una respuesta" : avatarState === "speaking" ? "Estoy hablando" : "Lista para conversar"}
            </span>
          </div>
        </div>

        <div className="chat-stream" aria-live="polite">
          {messages.length === 0 ? (
            <div className="chat-empty">
              <TutorAvatar profile={avatarProfile} state={avatarState} />
              <h2>Hola, {learnerName}. Soy {avatarProfile.name}.</h2>
              <p className="muted">Escribe o dicta una frase en el idioma que estás aprendiendo. Te responderé y corregiré cuando haga falta.</p>
              <div className="prompt-chips">
                <button type="button" onClick={() => setDraft(starterPrompts[0])}>Probar una corrección</button>
                <button type="button" onClick={() => setDraft(starterPrompts[1])}>Conversación libre</button>
              </div>
            </div>
          ) : (
            messages.map((message) => (
              <article key={message.id} className={`chat-message chat-message-${message.role}`}>
                <div className="message-bubble">
                  <div className="message-header-row">
                    <span className="message-role">{message.role === "user" ? "Tú" : avatarProfile.name}</span>
                    {message.role === "assistant" && message.id === latestAssistantId ? (
                      <button
                        className={`message-audio-button${speech.speaking ? " is-active" : ""}`}
                        type="button"
                        onClick={() => {
                          if (speech.speaking) speech.stopSpeaking();
                          else speakAsTutor(message.content);
                        }}
                        disabled={!speech.synthesisSupported}
                        aria-pressed={speech.speaking}
                      >
                        {speech.speaking ? "■ Detener" : "🔊 Escuchar"}
                      </button>
                    ) : null}
                  </div>
                  <p>{message.content}</p>
                </div>
                {message.role === "assistant" && (message.corrected_text || message.explanation || message.translation) ? (
                  <div className="feedback-card">
                    {message.corrected_text ? (
                      <div><span>Corrección</span><strong>{message.corrected_text}</strong></div>
                    ) : null}
                    {message.explanation ? (
                      <div><span>Explicación</span><p>{message.explanation}</p></div>
                    ) : null}
                    {message.translation ? (
                      <div><span>Apoyo</span><p>{message.translation}</p></div>
                    ) : null}
                  </div>
                ) : null}
              </article>
            ))
          )}
          {loading ? <p className="typing-indicator">{avatarProfile.name} está pensando…</p> : null}
        </div>

        <form className="chat-composer" onSubmit={submit}>
          <label className="sr-only" htmlFor="tutor-message">Mensaje para el tutor</label>
          <textarea
            id="tutor-message"
            value={draft}
            onChange={(event) => {
              setDraft(event.target.value);
              speech.clearSpeechMessage();
            }}
            maxLength={2000}
            placeholder={speech.listening ? "Escuchando… habla ahora" : `Escribe o dicta para ${avatarProfile.name}…`}
            rows={3}
          />
          {speech.speechMessage ? <p className="voice-status" role="status">{speech.speechMessage}</p> : null}
          {error ? <p className="form-error" role="alert">{error}</p> : null}
          <div className="composer-actions">
            <span className="muted">{draft.length}/2000</span>
            <div className="composer-button-group">
              <button
                className={`button button-secondary${speech.listening ? " voice-button-active" : ""}`}
                type="button"
                onClick={toggleDictation}
                disabled={!speech.recognitionSupported || loading}
                aria-pressed={speech.listening}
              >
                {speech.listening ? "■ Detener" : "🎙 Dictar"}
              </button>
              <button className="button button-primary" type="submit" disabled={!canSend}>
                {loading ? "Enviando…" : "Enviar"}
              </button>
            </div>
          </div>
        </form>
      </section>
    </div>
  );
}
