import type { ReactNode } from "react";

interface BadgeProps {
  tone?: "neutral" | "success" | "danger";
  children: ReactNode;
}

export function Badge({ tone = "neutral", children }: BadgeProps) {
  const className = tone === "neutral" ? "badge" : `badge badge-${tone}`;
  return <span className={className}>{children}</span>;
}
