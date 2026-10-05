import type { Metadata, Viewport } from "next";
import Link from "next/link";
import type { ReactNode } from "react";
import { MobileNav } from "@/components/navigation/MobileNav";
import { PwaClient } from "@/components/pwa/PwaClient";
import { getCurrentUser } from "@/lib/server-auth";

import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "LinguaAI Coach",
    template: "%s · LinguaAI Coach",
  },
  applicationName: "LinguaAI Coach",
  description: "Tu coach de idiomas con IA: español, inglés y serbio.",
  manifest: "/manifest.webmanifest",
  icons: {
    icon: [
      { url: "/icons/icon-192.png", sizes: "192x192", type: "image/png" },
      { url: "/icons/icon-512.png", sizes: "512x512", type: "image/png" },
    ],
    apple: [{ url: "/icons/apple-touch-icon.png", sizes: "180x180", type: "image/png" }],
  },
  appleWebApp: {
    capable: true,
    title: "LinguaAI",
    statusBarStyle: "default",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
  themeColor: "#4f46e5",
};

export default async function RootLayout({ children }: { children: ReactNode }) {
  const user = await getCurrentUser();

  return (
    <html lang="es">
      <body className={user ? "has-mobile-nav" : undefined}>
        <header className="site-header">
          <div className="header-inner">
            <Link className="logo" href={user ? "/dashboard" : "/"}>LinguaAI Coach</Link>
            <nav className="site-nav" aria-label="Navegación principal">
              {user ? (
                <>
                  <Link href="/tutor">Tutor</Link>
                  <Link href="/translator">Traductor</Link>
                  <Link href="/pronunciation">Pronunciación</Link>
                  <Link href="/history">Historial</Link>
                  <Link href="/progress">Progreso</Link>
                  <Link href="/plans">Planes</Link>
                  <Link href="/account">Cuenta</Link>
                  {user.is_superuser ? <Link href="/admin">Admin</Link> : null}
                  <Link className="button button-primary button-small" href="/dashboard">Panel</Link>
                </>
              ) : (
                <>
                  <Link href="/plans">Planes</Link>
                  <Link href="/login">Ingresar</Link>
                  <Link className="button button-primary button-small" href="/register">Crear cuenta</Link>
                </>
              )}
            </nav>
          </div>
        </header>
        <main className="container">{children}</main>
        <footer className="site-footer"><span>© {new Date().getFullYear()} LinguaAI Coach</span><span className="footer-links"><Link href="/privacy">Privacidad</Link><Link href="/terms">Términos</Link><Link href="/cookies">Cookies</Link></span></footer>
        {user ? <MobileNav isAdmin={Boolean(user.is_superuser)} /> : null}
        <PwaClient />
      </body>
    </html>
  );
}
