# LinguaAI Coach — revisión v0.2.0

## Objetivo
Completar el flujo de acceso del estudiante sin modificar el backend consolidado.

## Archivos añadidos
- `apps/web/src/lib/server-auth.ts`
- `apps/web/src/app/api/session/login/route.ts`
- `apps/web/src/app/api/session/register/route.ts`
- `apps/web/src/app/api/session/logout/route.ts`
- `apps/web/src/app/api/session/me/route.ts`
- `apps/web/src/app/api/session/onboarding/route.ts`
- `apps/web/src/app/login/page.tsx`
- `apps/web/src/app/register/page.tsx`
- `apps/web/src/app/onboarding/page.tsx`
- `apps/web/src/app/dashboard/page.tsx`
- `apps/web/src/components/auth/LoginForm.tsx`
- `apps/web/src/components/auth/RegisterForm.tsx`
- `apps/web/src/components/onboarding/OnboardingForm.tsx`
- `apps/web/src/components/dashboard/LogoutButton.tsx`

## Archivos modificados
- `apps/web/src/app/layout.tsx`
- `apps/web/src/app/page.tsx`
- `apps/web/src/app/globals.css`
- `README.md`

## Seguridad de sesión
El token JWT emitido por FastAPI se almacena en una cookie HttpOnly en la aplicación Next.js. Las páginas protegidas validan la sesión contra `/api/v1/auth/me`. Esto evita guardar el JWT en `localStorage`.

## Validación realizada
- Revisión estática de contratos con los endpoints existentes del backend.
- El backend no fue modificado.
- Se intentó instalar las dependencias Node para ejecutar `tsc` y `next build`, pero la instalación del entorno agotó el tiempo disponible y dejó `node_modules` incompleto. Por ello el typecheck/build no se reporta como aprobado en este entorno.

## Prueba recomendada en el equipo local
1. `cp .env.example .env` y reemplazar `POSTGRES_PASSWORD` y `SECRET_KEY`.
2. `make up`.
3. Abrir `http://localhost:3000/register`.
4. Crear una cuenta y completar onboarding.
5. Confirmar redirección a `/dashboard` y luego probar cierre de sesión/login.
