"""FastAPI application factory for LinguaAI Coach."""

import logging

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.health import router as health_router
from app.domains.admin.router import router as admin_router
from app.domains.auth.router import router as auth_router
from app.domains.billing.router import router as billing_router
from app.domains.languages.router import router as languages_router
from app.domains.lessons.router import router as lessons_router
from app.domains.tutor.router import router as tutor_router
from app.domains.translation.router import router as translation_router
from app.domains.pronunciation.router import router as pronunciation_router
from app.domains.users.router import router as users_router

logging.basicConfig(level=logging.DEBUG if settings.debug else logging.INFO)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        # Hide interactive docs in production by default.
        docs_url=None if settings.is_production else "/docs",
        redoc_url=None if settings.is_production else "/redoc",
        openapi_url=None if settings.is_production else "/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

    @app.middleware("http")
    async def security_headers(request: Request, call_next) -> Response:
        response: Response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        return response

    app.include_router(health_router)
    for router in (auth_router, users_router, admin_router, billing_router, languages_router, lessons_router, tutor_router, translation_router, pronunciation_router):
        app.include_router(router, prefix=settings.api_v1_prefix)

    return app


app = create_app()
