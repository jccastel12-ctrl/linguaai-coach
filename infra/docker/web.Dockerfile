# syntax=docker/dockerfile:1
# Build context: repository root (needed for npm workspaces + packages/shared-types).

FROM node:20-alpine AS deps
WORKDIR /repo
COPY package.json package-lock.json ./
COPY apps/web/package.json apps/web/package.json
COPY packages/shared-types/package.json packages/shared-types/package.json
RUN npm ci --no-audit --no-fund

# ---- dev: next dev with hot reload (sources are bind-mounted by compose) ----
FROM deps AS dev
ENV NEXT_TELEMETRY_DISABLED=1
COPY apps/web apps/web
COPY packages packages
WORKDIR /repo/apps/web
EXPOSE 3000
CMD ["npm", "run", "dev"]

# ---- build ----
FROM deps AS build
# NEXT_PUBLIC_* values are inlined into the client bundle at build time.
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_TELEMETRY_DISABLED=1 NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
COPY apps/web apps/web
COPY packages packages
RUN npm run build --workspace @linguaai/web

# ---- prod: minimal standalone server, non-root ----
FROM node:20-alpine AS prod
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1 PORT=3000 HOSTNAME=0.0.0.0
WORKDIR /app
RUN addgroup -S app && adduser -S app -G app
COPY --from=build --chown=app:app /repo/apps/web/.next/standalone ./
COPY --from=build --chown=app:app /repo/apps/web/.next/static ./apps/web/.next/static
USER app
EXPOSE 3000
CMD ["node", "apps/web/server.js"]
