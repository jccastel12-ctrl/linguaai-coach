# LinguaAI Coach v1.0.0 — administración y preparación de facturación

Fecha: 2026-10-04

## Alcance

Esta versión añade una capa administrativa funcional sobre el MVP v0.9 y deja el modelo de suscripción preparado para integrar un proveedor de pagos más adelante. **No procesa cobros reales ni webhooks.**

## Backend

- Nuevo dominio `admin` protegido por `is_superuser`.
- `GET /api/v1/admin/overview`: usuarios, cuentas activas, usuarios Pro, solicitudes pendientes, altas de 7 días y uso diario agregado.
- `GET /api/v1/admin/users`: listado y búsqueda de cuentas; filtro de solicitudes Pro.
- `PATCH /api/v1/admin/users/{id}/subscription`: cambio manual Basic/Pro con estado de suscripción.
- `PATCH /api/v1/admin/users/{id}/active`: activar/desactivar cuentas; impide que un administrador se desactive a sí mismo.
- `GET /api/v1/admin/audit`: últimos cambios administrativos.
- Nuevo `BillingAuditEvent` para trazabilidad de cambios manuales.
- `subscriptions` reserva campos para proveedor, customer id, subscription id, fin de periodo y cancelación al final del periodo.
- `GET /api/v1/billing/payment-capabilities` informa de forma explícita que checkout/webhooks están deshabilitados.
- Nueva migración Alembic `005_admin_payment_readiness.py`.
- Script seguro para promover una cuenta existente: `python -m app.scripts.promote_admin <email>`.

## Web

- Nueva página protegida `/admin`.
- Métricas principales del producto.
- Lista de solicitudes Pro pendientes.
- Tabla de usuarios y estado de cuenta.
- Acciones manuales para otorgar Pro, volver a Basic, desactivar o reactivar cuentas.
- Vista de auditoría de cambios.
- Enlace `Admin` visible únicamente a usuarios con `is_superuser=true`.
- La página de planes muestra el estado real de capacidades de pago.

## Configuración de pagos

Se añaden variables de entorno preparatorias:

- `PAYMENT_PROVIDER=disabled`
- `STRIPE_SECRET_KEY=`
- `STRIPE_WEBHOOK_SECRET=`
- `STRIPE_PRICE_ID_PRO=`
- `APP_PUBLIC_URL=`

Estas variables **no activan pagos en v1.0**. La integración real de Stripe u otro proveedor debe implementarse y validarse como una fase independiente.

## Pruebas añadidas

- Rechazo de acceso admin a usuarios normales.
- Acceso y métricas del panel admin.
- Aprobación manual de solicitud Pro.
- Persistencia de auditoría del cambio de plan.
- Listado/filtro de solicitudes.
- Protección contra auto-desactivación del administrador.
- Endpoint de capacidades de pago deshabilitadas.
