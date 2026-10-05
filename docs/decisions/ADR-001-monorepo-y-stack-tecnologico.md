# ADR-001: Monorepo y stack tecnológico

- **Estado**: Aceptado
- **Fecha**: 2026-10-01
- **Decisores**: Equipo fundador de LinguaAI Coach

## Contexto

LinguaAI Coach es una plataforma SaaS de aprendizaje de idiomas (español, inglés, serbio) que incorporará funciones de IA (corrección, tutor conversacional, práctica oral). En la fase inicial el equipo es pequeño y necesita:

- Iterar rápido sobre web y API a la vez, con contratos coherentes entre ambas.
- Un ecosistema maduro para IA/ML en el backend.
- Despliegue local reproducible en un solo comando.
- Seguridad razonable desde el día uno.

## Decisión

1. **Monorepo** con `apps/web`, `apps/api`, `packages/shared-types`, `infra/` y `docs/`, usando npm workspaces para la parte TypeScript.
2. **Backend en Python con FastAPI**, organizado como **monolito modular por dominios** (`auth`, `users`, `languages`, `lessons`).
3. **PostgreSQL** como base de datos principal, con **SQLAlchemy 2.0** y migraciones **Alembic** escritas/revisadas en el repositorio.
4. **Frontend en Next.js (App Router) + TypeScript estricto**.
5. **Docker Compose** para desarrollo local; **Redis** opcional (perfil) para futuras colas/rate limiting.
6. **JWT + Argon2id** para autenticación inicial.
7. Tipos compartidos mantenidos **manualmente** en `packages/shared-types` en esta fase.

## Alternativas consideradas

| Alternativa | Motivo de descarte |
|-------------|--------------------|
| Repos separados (polyrepo) | Más fricción para cambios que cruzan web/API; versionado de contratos prematuro |
| Backend en Node (NestJS) | Un solo lenguaje, pero el ecosistema de IA/NLP en Python es superior y lo necesitaremos |
| Microservicios desde el inicio | Complejidad operativa injustificada para el tamaño actual; los dominios permiten extraer servicios después |
| Django + DRF | Más pesado; FastAPI ofrece async, OpenAPI nativo y Pydantic, útil para integrar LLMs |
| MongoDB | El dominio (usuarios, progreso, niveles) es relacional; JSON de Postgres cubre el contenido flexible |
| Turborepo/Nx | Útiles a mayor escala; npm workspaces + Makefile bastan por ahora |
| bcrypt (passlib) | Argon2id es la recomendación actual de OWASP y no tiene el límite de 72 bytes |

## Consecuencias

**Positivas**
- Un PR puede cambiar API, tipos y web de forma atómica; una sola CI.
- OpenAPI generado automáticamente por FastAPI facilita clientes y documentación.
- Límites de dominio claros desde el inicio, preparados para una futura extracción del módulo de IA.

**Negativas / riesgos**
- Dos toolchains (Python y Node) en el mismo repo.
- Los tipos compartidos pueden desincronizarse de los esquemas Pydantic → **mitigación**: generar `shared-types` desde `/openapi.json` (p. ej. `openapi-typescript`) en una iteración próxima y validarlo en CI.
- La CI crecerá con el repo → evaluar ejecución selectiva por rutas (`paths` filters) o Turborepo cuando sea necesario.

## Revisión

Revisar esta decisión al superar ~5 desarrolladores en paralelo, o cuando el módulo de IA requiera escalado independiente.
