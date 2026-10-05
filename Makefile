# LinguaAI Coach — common developer commands. Run `make help` for the list.

SHELL := /bin/bash
COMPOSE := docker compose
API_DIR := apps/api
PY ?= python3
VENV := $(API_DIR)/.venv
VENV_BIN := $(VENV)/bin

.DEFAULT_GOAL := help

.PHONY: help
help: ## Muestra esta ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

.env:
	@cp .env.example .env
	@echo ">> .env creado desde .env.example. Revisa y cambia los valores 'change-me' antes de continuar."

# ---------- Docker ----------
.PHONY: up up-redis down down-v logs ps build
up: .env ## Levanta postgres + api + web
	$(COMPOSE) up -d --build

up-redis: .env ## Levanta el stack incluyendo Redis (opcional)
	$(COMPOSE) --profile redis up -d --build

down: ## Detiene los contenedores
	$(COMPOSE) --profile redis down

down-v: ## Detiene y BORRA volúmenes (datos de Postgres)
	$(COMPOSE) --profile redis down -v

logs: ## Sigue los logs de todos los servicios
	$(COMPOSE) logs -f

ps: ## Estado de los servicios
	$(COMPOSE) ps

build: ## Reconstruye las imágenes
	$(COMPOSE) build

# ---------- Base de datos ----------
.PHONY: migrate migration downgrade seed db-shell promote-admin
migrate: ## Aplica migraciones (alembic upgrade head) en el contenedor api
	$(COMPOSE) exec api alembic upgrade head

migration: ## Crea una migración autogenerada: make migration m="descripcion"
	@test -n "$(m)" || (echo 'Uso: make migration m="descripcion"' && exit 1)
	$(COMPOSE) exec api alembic revision --autogenerate -m "$(m)"

downgrade: ## Revierte la última migración
	$(COMPOSE) exec api alembic downgrade -1

seed: ## Inserta lecciones de ejemplo (solo desarrollo)
	$(COMPOSE) exec api python -m app.scripts.seed

db-shell: ## Abre psql dentro del contenedor de Postgres
	$(COMPOSE) exec postgres sh -c 'psql -U $$POSTGRES_USER -d $$POSTGRES_DB'

promote-admin: ## Da rol admin a un usuario existente: make promote-admin e="admin@dominio.com"
	@test -n "$(e)" || (echo 'Uso: make promote-admin e="admin@dominio.com"' && exit 1)
	$(COMPOSE) exec api python -m app.scripts.promote_admin "$(e)"

# ---------- Desarrollo local sin Docker ----------
.PHONY: install install-api install-web api-dev web-dev
install: install-api install-web ## Instala dependencias de API (venv) y web (npm)

install-api: ## Crea venv e instala dependencias Python
	$(PY) -m venv $(VENV)
	$(VENV_BIN)/pip install -r $(API_DIR)/requirements-dev.txt

install-web: ## Instala dependencias npm (workspaces)
	npm install

api-dev: ## Ejecuta la API localmente con recarga
	cd $(API_DIR) && .venv/bin/uvicorn app.main:app --reload --port 8000

web-dev: ## Ejecuta la web localmente
	npm run dev:web

# ---------- Calidad ----------
.PHONY: test test-api test-web lint lint-api lint-web format typecheck
test: test-api test-web ## Ejecuta todos los tests

test-api: ## Tests de la API (pytest, SQLite en memoria)
	cd $(API_DIR) && .venv/bin/pytest

test-web: typecheck ## Verificación de la web (typecheck; añadir tests de UI más adelante)

lint: lint-api lint-web ## Lint de todo el monorepo

lint-api: ## Ruff (lint + formato) en la API
	cd $(API_DIR) && .venv/bin/ruff check . && .venv/bin/ruff format --check .

lint-web: ## ESLint en la web
	npm run lint

format: ## Formatea el código Python
	cd $(API_DIR) && .venv/bin/ruff format . && .venv/bin/ruff check --fix .

typecheck: ## Typecheck TypeScript de todos los workspaces
	npm run typecheck

# ---------- Producción (Docker Compose + Caddy) ----------
PROD_COMPOSE := docker compose --env-file .env.production -f compose.production.yml

.PHONY: prod-preflight prod-build prod-migrate prod-up prod-down prod-logs prod-ps prod-smoke prod-backup
prod-preflight: ## Valida .env.production antes de desplegar
	./scripts/preflight-production.sh .env.production

prod-build: prod-preflight ## Construye imágenes de producción
	$(PROD_COMPOSE) build

prod-migrate: prod-preflight ## Aplica migraciones como tarea única
	$(PROD_COMPOSE) run --rm api alembic upgrade head

prod-up: prod-preflight ## Levanta el stack de producción
	$(PROD_COMPOSE) up -d

prod-down: ## Detiene el stack de producción sin borrar datos
	$(PROD_COMPOSE) down

prod-logs: ## Sigue logs del stack de producción
	$(PROD_COMPOSE) logs -f

prod-ps: ## Estado de servicios de producción
	$(PROD_COMPOSE) ps

prod-smoke: prod-preflight ## Verifica web + health + readiness públicos
	./scripts/smoke-production.sh .env.production

prod-backup: prod-preflight ## Crea backup manual de PostgreSQL en backups/
	./scripts/backup-postgres.sh .env.production backups

.PHONY: staging-smoke
staging-smoke: ## Smoke test staging: make staging-smoke web=https://... api=https://...
	@test -n "$(web)" -a -n "$(api)" || (echo 'Uso: make staging-smoke web="https://..." api="https://..."' && exit 1)
	./scripts/smoke-staging.sh "$(web)" "$(api)"
