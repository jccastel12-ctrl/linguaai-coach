"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { LanguageCode } from "@/types";

const speechLocales: Record<LanguageCode, string> = {
  es: "es-ES",
  en: "en-US",
  sr: "sr-RS",
};

interface RecognitionAlternativeLike {
  transcript: string;
}

interface RecognitionResultLike {
  isFinal: boolean;
  length: number;
  [index: number]: RecognitionAlternativeLike;
}

interface RecognitionEventLike {
  resultIndex: number;
  results: {
    length: number;
    [index: number]: RecognitionResultLike;
  };
}

interface RecognitionErrorLike {
  error: string;
}

interface RecognitionLike {
  lang: string;
  interimResults: boolean;
  continuous: boolean;
  maxAlternatives: number;
  start(): void;
  stop(): void;
  abort(): void;
  onresult: ((event: RecognitionEventLike) => void) | null;
  onerror: ((event: RecognitionErrorLike) => void) | null;
  onend: (() => void) | null;
}

type RecognitionConstructor = new () => RecognitionLike;

type SpeechWindow = Window & {
  SpeechRecognition?: RecognitionConstructor;
  webkitSpeechRecognition?: RecognitionConstructor;
};

function getRecognitionConstructor(): RecognitionConstructor | null {
  if (typeof window === "undefined") return null;
  const speechWindow = window as SpeechWindow;
  return speechWindow.SpeechRecognition ?? speechWindow.webkitSpeechRecognition ?? null;
}

function messageForRecognitionError(code: string): string {
  if (code === "not-allowed" || code === "service-not-allowed") return "Permite el acceso al micrófono para usar el dictado.";
  if (code === "no-speech") return "No detecté voz. Intenta hablar un poco más cerca del micrófono.";
  if (code === "audio-capture") return "No encontré un micrófono disponible.";
  if (code === "network") return "El reconocimiento de voz del navegador no está disponible en este momento.";
  return "No fue posible reconocer la voz. Intenta nuevamente.";
}

function normalizedLanguage(code: string): LanguageCode {
  if (code === "es" || code === "sr") return code;
  return "en";
}

interface SpeechPlaybackOptions {
  rate?: number;
  pitch?: number;
}

export function useBrowserSpeech() {
  const recognitionRef = useRef<RecognitionLike | null>(null);
  const [recognitionSupported, setRecognitionSupported] = useState(false);
  const [synthesisSupported, setSynthesisSupported] = useState(false);
  const [listening, setListening] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const [speechMessage, setSpeechMessage] = useState("");

  useEffect(() => {
    setRecognitionSupported(Boolean(getRecognitionConstructor()));
    setSynthesisSupported(typeof window !== "undefined" && "speechSynthesis" in window && "SpeechSynthesisUtterance" in window);

    return () => {
      recognitionRef.current?.abort();
      recognitionRef.current = null;
      if (typeof window !== "undefined" && "speechSynthesis" in window) window.speechSynthesis.cancel();
    };
  }, []);

  const stopListening = useCallback(() => {
    recognitionRef.current?.stop();
    setListening(false);
  }, []);

  const startListening = useCallback((
    languageCode: string,
    initialText: string,
    onText: (text: string) => void,
  ) => {
    const Recognition = getRecognitionConstructor();
    if (!Recognition) {
      setSpeechMessage("Tu navegador no ofrece dictado por voz. Prueba una versión reciente de Chrome, Edge o Safari.");
      return;
    }

    recognitionRef.current?.abort();
    const recognition = new Recognition();
    recognitionRef.current = recognition;
    const baseText = initialText.trim();

    recognition.lang = speechLocales[normalizedLanguage(languageCode)];
    recognition.interimResults = true;
    recognition.continuous = false;
    recognition.maxAlternatives = 1;

    recognition.onresult = (event) => {
      const finalParts: string[] = [];
      const interimParts: string[] = [];
      for (let index = 0; index < event.results.length; index += 1) {
        const result = event.results[index];
        const transcript = result?.[0]?.transcript?.trim();
        if (!transcript) continue;
        if (result.isFinal) finalParts.push(transcript);
        else interimParts.push(transcript);
      }
      const spoken = [...finalParts, ...interimParts].join(" ").trim();
      const combined = [baseText, spoken].filter(Boolean).join(baseText && spoken ? " " : "");
      onText(combined);
    };

    recognition.onerror = (event) => {
      setSpeechMessage(messageForRecognitionError(event.error));
      setListening(false);
    };

    recognition.onend = () => {
      setListening(false);
      recognitionRef.current = null;
    };

    try {
      setSpeechMessage("");
      setListening(true);
      recognition.start();
    } catch {
      setListening(false);
      setSpeechMessage("El micrófono ya está ocupado. Detén la escucha e inténtalo de nuevo.");
    }
  }, []);

  const stopSpeaking = useCallback(() => {
    if (typeof window !== "undefined" && "speechSynthesis" in window) window.speechSynthesis.cancel();
    setSpeaking(false);
  }, []);

  const speak = useCallback((text: string, languageCode: string, options: SpeechPlaybackOptions = {}) => {
    if (typeof window === "undefined" || !("speechSynthesis" in window) || !("SpeechSynthesisUtterance" in window)) {
      setSpeechMessage("Tu navegador no permite reproducir voz sintetizada.");
      return;
    }
    if (!text.trim()) return;

    const language = normalizedLanguage(languageCode);
    const locale = speechLocales[language];
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = locale;
    utterance.rate = Math.min(1.2, Math.max(0.75, options.rate ?? 0.95));
    utterance.pitch = Math.min(1.25, Math.max(0.75, options.pitch ?? 1));

    const voices = window.speechSynthesis.getVoices();
    const exactVoice = voices.find((voice) => voice.lang.toLowerCase() === locale.toLowerCase());
    const languageVoice = voices.find((voice) => voice.lang.toLowerCase().startsWith(language));
    utterance.voice = exactVoice ?? languageVoice ?? null;

    utterance.onstart = () => {
      setSpeechMessage("");
      setSpeaking(true);
    };
    utterance.onend = () => setSpeaking(false);
    utterance.onerror = () => {
      setSpeaking(false);
      setSpeechMessage("No fue posible reproducir el audio con la voz instalada en este dispositivo.");
    };

    window.speechSynthesis.speak(utterance);
  }, []);

  return {
    recognitionSupported,
    synthesisSupported,
    listening,
    speaking,
    speechMessage,
    startListening,
    stopListening,
    speak,
    stopSpeaking,
    clearSpeechMessage: () => setSpeechMessage(""),
  };
}
