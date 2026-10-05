import Link from "next/link";
import { UpgradeRequestButton } from "@/components/billing/UpgradeRequestButton";
import { getBillingOverview, getPaymentCapabilities, getPlans } from "@/lib/billing-server";
import { getCurrentUser } from "@/lib/server-auth";
import type { FeatureUsage, PlanInfo } from "@/types";

function usagePercent(item: FeatureUsage): number {
  if (item.limit <= 0) return 0;
  return Math.min(100, Math.round((item.used / item.limit) * 100));
}

function PlanCard({ plan, current }: { plan: PlanInfo; current: boolean }) {
  return (
    <article className={`plan-card${current ? " plan-card-current" : ""}`}>
      <div className="plan-card-heading">
        <div>
          <span className="card-label">{current ? "Tu plan actual" : "Plan disponible"}</span>
          <h2>{plan.name}</h2>
        </div>
        {current ? <span className="plan-badge">Activo</span> : null}
      </div>
      <p>{plan.tagline}</p>
      <p className="muted">{plan.audience}</p>
      <div className="plan-limits">
        <div><strong>{plan.limits.tutor_messages_per_day}</strong><span>mensajes al tutor / día</span></div>
        <div><strong>{plan.limits.translations_per_day}</strong><span>traducciones / día</span></div>
        <div><strong>{plan.limits.pronunciation_attempts_per_day}</strong><span>intentos de pronunciación / día</span></div>
      </div>
      <ul className="plan-benefits">
        {plan.benefits.map((benefit) => <li key={benefit}>✓ {benefit}</li>)}
      </ul>
      {!plan.payment_enabled && plan.id === "pro" ? (
        <p className="plan-payment-note">Checkout y cobro aún no están habilitados; la estructura comercial ya está preparada.</p>
      ) : null}
    </article>
  );
}

export default async function PlansPage() {
  const [user, plans, paymentCapabilities] = await Promise.all([getCurrentUser(), getPlans(), getPaymentCapabilities()]);
  const billing = user ? await getBillingOverview() : null;
  const fallbackPlans: PlanInfo[] = plans.length ? plans : [
    {
      id: "basic", name: "Basic", tagline: "Aprende y practica cada día.", audience: "Uso regular.",
      limits: { tutor_messages_per_day: 20, translations_per_day: 30, pronunciation_attempts_per_day: 10 },
      benefits: ["Tutor IA", "Traductor", "Pronunciación", "Progreso"], payment_enabled: false,
    },
    {
      id: "pro", name: "Pro", tagline: "Mayor capacidad diaria.", audience: "Uso intensivo.",
      limits: { tutor_messages_per_day: 200, translations_per_day: 500, pronunciation_attempts_per_day: 100 },
      benefits: ["Todo Basic", "Límites ampliados", "Preparado para funciones premium"], payment_enabled: false,
    },
  ];

  return (
    <section className="plans-shell">
      <div className="plans-hero">
        <span className="eyebrow">Planes LinguaAI Coach</span>
        <h1>Elige cuánto quieres practicar.</h1>
        <p>Basic cubre una rutina diaria normal. Pro amplía la capacidad para aprendizaje intensivo y deja lista la cuenta para futuras funciones premium.</p>
      </div>

      <div className="plans-grid">
        {fallbackPlans.map((plan) => <PlanCard key={plan.id} plan={plan} current={billing?.plan.id === plan.id} />)}
      </div>

      {paymentCapabilities && !paymentCapabilities.checkout_enabled ? (
        <div className="notice-card">
          <div>
            <strong>Checkout todavía desactivado</strong>
            <p className="muted">{paymentCapabilities.note} Proveedor configurado: {paymentCapabilities.provider}.</p>
          </div>
        </div>
      ) : null}

      {user && billing ? (
        <section className="usage-card">
          <div className="section-heading-row compact">
            <div>
              <span className="eyebrow">Uso de hoy</span>
              <h2>Plan {billing.plan.name}</h2>
              <p className="muted">Los contadores se reinician diariamente. Esta fase usa UTC como referencia operativa.</p>
            </div>
            {billing.plan.id === "basic" ? <UpgradeRequestButton alreadyRequested={billing.requested_plan === "pro"} /> : null}
          </div>
          <div className="usage-list">
            {billing.usage.map((item) => (
              <div className="usage-item" key={item.feature}>
                <div className="usage-item-heading"><strong>{item.label}</strong><span>{item.used} / {item.limit}</span></div>
                <div className="usage-track" aria-label={`${item.label}: ${item.used} de ${item.limit}`}><span style={{ width: `${usagePercent(item)}%` }} /></div>
                <small>{item.remaining} disponibles hoy</small>
              </div>
            ))}
          </div>
        </section>
      ) : (
        <div className="notice-card">
          <div><strong>Consulta tu consumo diario desde tu cuenta</strong><p className="muted">Crea una cuenta para usar Basic y ver tus límites disponibles.</p></div>
          <Link className="button button-primary" href="/register">Crear cuenta</Link>
        </div>
      )}
    </section>
  );
}
