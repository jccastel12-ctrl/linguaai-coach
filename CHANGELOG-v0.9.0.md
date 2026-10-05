# LinguaAI Coach v0.9.0 — Planes Basic/Pro y control de uso

## Añadido

- Dominio `billing` en FastAPI con catálogo de planes, suscripción por usuario y medición de consumo.
- Plan Basic como nivel inicial y plan Pro preparado para monetización posterior.
- Migración Alembic `004_billing_usage_limits.py` con tablas `subscriptions` y `usage_events`.
- Límites diarios para Tutor IA, Traducción y Pronunciación.
- Respuesta HTTP 429 al alcanzar la cuota de una función.
- Registro de consumo solo después de una operación exitosa.
- Endpoint público `GET /api/v1/billing/plans`.
- Endpoint autenticado `GET /api/v1/billing/me`.
- Endpoint `POST /api/v1/billing/me/request-upgrade` para registrar intención de pasar a Pro sin simular un pago.
- Página `/plans` con comparación Basic/Pro, consumo diario y solicitud Pro.
- Tarjeta de plan en el dashboard y enlace “Planes” en la navegación.
- Nuevos contratos TypeScript compartidos para planes, uso y suscripción.

## Límites configurados en v0.9

### Basic
- 20 mensajes al Tutor IA por día.
- 30 traducciones por día.
- 10 intentos de pronunciación por día.

### Pro
- 200 mensajes al Tutor IA por día.
- 500 traducciones por día.
- 100 intentos de pronunciación por día.

Los valores son configuración inicial de producto y pueden ajustarse antes de conectar pagos.

## Fuera de alcance

- Stripe, Mercado Pago u otro checkout real.
- Renovaciones, facturas, impuestos o webhooks de pago.
- Activación automática de Pro después de pagar.
- Precios definitivos.

La versión evita presentar una suscripción como pagada cuando aún no existe un proveedor de cobro conectado.
