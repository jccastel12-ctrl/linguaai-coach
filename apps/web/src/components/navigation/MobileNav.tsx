"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { LogoutButton } from "@/components/dashboard/LogoutButton";

const primaryItems = [
  { href: "/dashboard", label: "Inicio", icon: "⌂" },
  { href: "/tutor", label: "Tutor", icon: "✦" },
  { href: "/translator", label: "Traducir", icon: "文" },
  { href: "/pronunciation", label: "Pronunciar", icon: "◉" },
];

export function MobileNav({ isAdmin = false }: { isAdmin?: boolean }) {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  return (
    <>
      {open ? (
        <div className="mobile-more-backdrop" onClick={() => setOpen(false)}>
          <div className="mobile-more-sheet" role="dialog" aria-modal="true" aria-label="Más opciones" onClick={(event) => event.stopPropagation()}>
            <div className="mobile-more-heading">
              <strong>Más opciones</strong>
              <button type="button" onClick={() => setOpen(false)} aria-label="Cerrar menú">×</button>
            </div>
            <nav className="mobile-more-links">
              <Link href="/history" onClick={() => setOpen(false)}>Historial</Link>
              <Link href="/progress" onClick={() => setOpen(false)}>Progreso</Link>
              <Link href="/plans" onClick={() => setOpen(false)}>Planes</Link>
              <Link href="/account" onClick={() => setOpen(false)}>Cuenta</Link>
              {isAdmin ? <Link href="/admin" onClick={() => setOpen(false)}>Administración</Link> : null}
              <LogoutButton />
            </nav>
          </div>
        </div>
      ) : null}

      <nav className="mobile-bottom-nav" aria-label="Navegación móvil">
        {primaryItems.map((item) => {
          const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
          return (
            <Link className={active ? "is-active" : undefined} href={item.href} key={item.href}>
              <span className="mobile-nav-icon" aria-hidden="true">{item.icon}</span>
              <span>{item.label}</span>
            </Link>
          );
        })}
        <button className={open ? "is-active" : undefined} type="button" onClick={() => setOpen(true)}>
          <span className="mobile-nav-icon" aria-hidden="true">•••</span>
          <span>Más</span>
        </button>
      </nav>
    </>
  );
}
