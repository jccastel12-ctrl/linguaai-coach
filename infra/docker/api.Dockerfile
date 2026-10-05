# syntax=docker/dockerfile:1
# Build context: repository root.

FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app
RUN groupadd --system app && useradd --system --gid app --home /app app

# ---- dev: hot reload, dev dependencies, runs migrations on start ----
FROM base AS dev
COPY apps/api/requirements.txt apps/api/requirements-dev.txt ./
RUN pip install -r requirements-dev.txt
COPY apps/api/ ./
COPY infra/docker/api-entrypoint.sh /usr/local/bin/api-entrypoint.sh
RUN chmod +x /usr/local/bin/api-entrypoint.sh
USER app
EXPOSE 8000
ENTRYPOINT ["api-entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ---- prod: runtime dependencies only, non-root, no reload ----
FROM base AS prod
COPY apps/api/requirements.txt ./
RUN pip install -r requirements.txt
COPY --chown=app:app apps/api/ ./
COPY infra/docker/api-entrypoint.sh /usr/local/bin/api-entrypoint.sh
RUN chmod +x /usr/local/bin/api-entrypoint.sh
USER app
EXPOSE 8000
ENTRYPOINT ["api-entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--workers", "2"]
