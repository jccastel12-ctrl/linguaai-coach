"""Resilient client for OpenAI-compatible chat-completions providers.

The client centralizes transient retry behavior and optional model fallback so
translation and tutor flows do not fail immediately on short provider outages
(429/5xx/timeouts). Secrets and prompt contents are never written to logs.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

_RETRYABLE_STATUS_CODES = {408, 425, 429, 500, 502, 503, 504}


class AIClientError(RuntimeError):
    """Base error for the shared AI client."""


class AIClientConfigurationError(AIClientError):
    """Credentials/model/request configuration is invalid."""


class AIClientUnavailableError(AIClientError):
    """Provider remained unavailable after retry/fallback attempts."""


@dataclass(slots=True)
class ChatCompletionResult:
    content: str
    model: str


class OpenAICompatibleChatClient:
    def __init__(self) -> None:
        self.api_key = settings.ai_api_key.get_secret_value() if settings.ai_api_key else ""
        if not self.api_key or not settings.ai_model:
            raise AIClientConfigurationError("AI_API_KEY/AI_MODEL is missing for the configured AI provider")

        self.base_url = settings.ai_base_url.rstrip("/")
        self.primary_model = settings.ai_model.strip()
        fallback = (settings.ai_fallback_model or "").strip()
        self.models = [self.primary_model]
        if fallback and fallback != self.primary_model:
            self.models.append(fallback)

    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        *,
        max_tokens: int,
        temperature: float | None = None,
    ) -> ChatCompletionResult:
        last_error: Exception | None = None

        async with httpx.AsyncClient(timeout=settings.ai_timeout_seconds) as client:
            for model_index, model in enumerate(self.models):
                for attempt in range(settings.ai_retry_attempts):
                    payload: dict[str, object] = {
                        "model": model,
                        "messages": messages,
                        "max_tokens": max_tokens,
                    }
                    # Current Gemini 3.x models deprecate sampling parameters.
                    # Keep them for other OpenAI-compatible providers only.
                    if temperature is not None and "generativelanguage.googleapis.com" not in self.base_url:
                        payload["temperature"] = temperature

                    try:
                        response = await client.post(
                            self.base_url + "/chat/completions",
                            headers={
                                "Authorization": f"Bearer {self.api_key}",
                                "Content-Type": "application/json",
                            },
                            json=payload,
                        )
                        response.raise_for_status()
                        content = str(response.json()["choices"][0]["message"]["content"]).strip()
                        if not content:
                            raise ValueError("empty completion content")
                        return ChatCompletionResult(content=content, model=model)
                    except httpx.HTTPStatusError as exc:
                        last_error = exc
                        status = exc.response.status_code
                        logger.warning(
                            "AI provider HTTP %s for model=%s attempt=%s/%s",
                            status,
                            model,
                            attempt + 1,
                            settings.ai_retry_attempts,
                        )

                        if status in (401, 403):
                            raise AIClientConfigurationError(
                                "El proveedor de IA rechazó la clave o el acceso configurado."
                            ) from exc
                        if status == 400:
                            raise AIClientConfigurationError(
                                "El proveedor de IA rechazó la solicitud configurada."
                            ) from exc
                        if status == 404:
                            # A fallback model can recover from a missing/retired model.
                            break
                        if status not in _RETRYABLE_STATUS_CODES:
                            raise AIClientError(f"El proveedor de IA devolvió HTTP {status}.") from exc
                    except (httpx.TimeoutException, httpx.NetworkError, httpx.RemoteProtocolError) as exc:
                        last_error = exc
                        logger.warning(
                            "AI provider network error for model=%s attempt=%s/%s",
                            model,
                            attempt + 1,
                            settings.ai_retry_attempts,
                        )
                    except (KeyError, TypeError, ValueError) as exc:
                        raise AIClientError("El proveedor de IA devolvió una respuesta inválida.") from exc

                    if attempt + 1 < settings.ai_retry_attempts:
                        delay = settings.ai_retry_backoff_seconds * (2**attempt)
                        if delay > 0:
                            await asyncio.sleep(delay)

                if model_index + 1 < len(self.models):
                    logger.warning("Switching to AI fallback model after primary model failure")

        raise AIClientUnavailableError(
            "El servicio de IA está temporalmente ocupado. LinguaAI reintentó automáticamente; "
            "vuelve a intentarlo en unos segundos."
        ) from last_error
