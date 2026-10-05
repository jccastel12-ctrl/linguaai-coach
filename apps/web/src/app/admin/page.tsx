import { redirect } from "next/navigation";
import { AdminUserActions } from "@/components/admin/AdminUserActions";
import { getAdminAudit, getAdminOverview, getAdminUsers, getPendingUpgrades } from "@/lib/admin-server";
import { getCurrentUser } from "@/lib/server-auth";

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("es-CO", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

export default async function AdminPage() {
  const user = await getCurrentUser();
  if (!user) redirect("/login");
  if (!user.is_superuser) redirect("/dashboard");

  const [overview, users, pending, audit] = await Promise.all([
    getAdminOverview(),
    getAdminUsers(),
    getPendingUpgrades(),
    getAdminAudit(),
  ]);

  if (!overview || !users || !pending) {
    return <div className="notice-card"><strong>No fue posible cargar el panel administrativo.</strong><p className="muted">Verifica que la API esté disponible y que tu cuenta conserve permisos de administrador.</p></div>;
  }

  return (
    <section className="admin-shell">
      <div className="admin-hero">
        <div>
          <span className="eyebrow">Administración</span>
          <h1>Control de usuarios y planes</h1>
          <p className="muted">Gestiona accesos, solicitudes Pro y métricas operativas. Los cambios de plan son manuales en v1.0 y quedan registrados en auditoría.</p>
        </div>
        <span className="admin-provider-badge">Pagos: {overview.payment_provider}</span>
      </div>

      <div className="admin-metrics">
        <article><span>Usuarios</span><strong>{overview.total_users}</strong><small>{overview.active_users} activos</small></article>
        <article><span>Plan Pro</span><strong>{overview.pro_users}</strong><small>{overview.pending_upgrade_requests} solicitudes pendientes</small></article>
        <article><span>Nuevos 7 días</span><strong>{overview.new_users_last_7_days}</strong><small>registros recientes</small></article>
        <article><span>Uso hoy</span><strong>{overview.usage_today.tutor_message + overview.usage_today.translation + overview.usage_today.pronunciation}</strong><small>acciones medidas</small></article>
      </div>

      {pending.items.length ? (
        <section className="admin-panel admin-pending-panel">
          <div className="section-heading-row compact"><div><span className="eyebrow">Pendientes</span><h2>Solicitudes de plan Pro</h2></div><span className="plan-badge">{pending.total}</span></div>
          <div className="admin-user-list">
            {pending.items.map((item) => (
              <div className="admin-user-row" key={item.id}>
                <div><strong>{item.full_name || item.email}</strong><span>{item.email}</span></div>
                <div><span className="admin-plan-pill">{item.plan_tier}</span></div>
                <AdminUserActions userId={item.id} currentPlan={item.plan_tier} requestedPlan={item.requested_plan} isActive={item.is_active} isSelf={item.id === user.id} />
              </div>
            ))}
          </div>
        </section>
      ) : null}

      <section className="admin-panel">
        <div className="section-heading-row compact"><div><span className="eyebrow">Usuarios</span><h2>Cuentas registradas</h2><p className="muted">Mostrando hasta 100 cuentas, ordenadas por fecha de registro.</p></div></div>
        <div className="admin-table-wrap">
          <table className="admin-table">
            <thead><tr><th>Usuario</th><th>Estado</th><th>Plan</th><th>Solicitud</th><th>Registro</th><th>Acciones</th></tr></thead>
            <tbody>
              {users.items.map((item) => (
                <tr key={item.id}>
                  <td><strong>{item.full_name || "Sin nombre"}</strong><small>{item.email}{item.is_superuser ? " · Admin" : ""}</small></td>
                  <td><span className={`admin-status ${item.is_active ? "is-active" : "is-inactive"}`}>{item.is_active ? "Activo" : "Inactivo"}</span></td>
                  <td><span className="admin-plan-pill">{item.plan_tier}</span></td>
                  <td>{item.requested_plan ? <span className="admin-request-pill">{item.requested_plan}</span> : "—"}</td>
                  <td><small>{formatDate(item.created_at)}</small></td>
                  <td><AdminUserActions userId={item.id} currentPlan={item.plan_tier} requestedPlan={item.requested_plan} isActive={item.is_active} isSelf={item.id === user.id} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="admin-panel">
        <div className="section-heading-row compact"><div><span className="eyebrow">Auditoría</span><h2>Cambios recientes</h2></div></div>
        {audit.length ? <div className="admin-audit-list">{audit.map((event) => (
          <div key={event.id}><strong>{event.action}</strong><span>{event.old_plan ?? "—"} → {event.new_plan ?? "—"}</span><small>{event.note || "Sin nota"} · {formatDate(event.created_at)}</small></div>
        ))}</div> : <p className="muted">Todavía no hay cambios administrativos registrados.</p>}
      </section>

      <div className="notice-card admin-payment-note"><div><strong>Preparado para pagos, sin cobros reales</strong><p className="muted">La suscripción ya reserva identificadores de proveedor/cliente/suscripción y periodo. Checkout y webhooks siguen desactivados hasta integrar y validar un proveedor de pagos.</p></div></div>
    </section>
  );
}
