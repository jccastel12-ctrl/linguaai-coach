"use client";

import { useEffect, useState } from "react";

type InstallPromptEvent = Event & {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: "accepted" | "dismissed"; platform: string }>;
};

function isIosDevice() {
  if (typeof navigator === "undefined") return false;
  return /iphone|ipad|ipod/i.test(navigator.userAgent);
}

function isStandalone() {
  if (typeof window === "undefined") return false;
  const iosStandalone = "standalone" in navigator && Boolean((navigator as Navigator & { standalone?: boolean }).standalone);
  return window.matchMedia("(display-mode: standalone)").matches || iosStandalone;
}

export function PwaClient() {
  const [installPrompt, setInstallPrompt] = useState<InstallPromptEvent | null>(null);
  const [showIosHelp, setShowIosHelp] = useState(false);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if ("serviceWorker" in navigator) {
      navigator.serviceWorker.register("/sw.js").catch(() => undefined);
    }

    if (isStandalone() || window.localStorage.getItem("linguaai-install-dismissed") === "1") {
      return;
    }

    if (isIosDevice()) {
      setVisible(true);
    }

    const onBeforeInstall = (event: Event) => {
      event.preventDefault();
      setInstallPrompt(event as InstallPromptEvent);
      setVisible(true);
    };

    const onInstalled = () => {
      setVisible(false);
      setInstallPrompt(null);
    };

    window.addEventListener("beforeinstallprompt", onBeforeInstall);
    window.addEventListener("appinstalled", onInstalled);
    return () => {
      window.removeEventListener("beforeinstallprompt", onBeforeInstall);
      window.removeEventListener("appinstalled", onInstalled);
    };
  }, []);

  async function install() {
    if (!installPrompt) {
      setShowIosHelp(true);
      return;
    }
    await installPrompt.prompt();
    const result = await installPrompt.userChoice;
    if (result.outcome === "accepted") {
      setVisible(false);
    }
    setInstallPrompt(null);
  }

  function dismiss() {
    window.localStorage.setItem("linguaai-install-dismissed", "1");
    setVisible(false);
  }

  if (!visible) return null;

  return (
    <aside className="pwa-install-banner" aria-label="Instalar LinguaAI Coach">
      <div>
        <strong>Usa LinguaAI como una app</strong>
        <p>
          {showIosHelp || (isIosDevice() && !installPrompt)
            ? "En iPhone/iPad: abre Compartir en Safari y elige “Añadir a pantalla de inicio”."
            : "Instálala en tu celular para abrirla desde la pantalla de inicio."}
        </p>
      </div>
      <div className="pwa-install-actions">
        <button className="button button-primary button-small" type="button" onClick={install}>
          {isIosDevice() && !installPrompt ? "Ver cómo" : "Instalar"}
        </button>
        <button className="pwa-dismiss" type="button" onClick={dismiss} aria-label="Cerrar aviso de instalación">×</button>
      </div>
    </aside>
  );
}
