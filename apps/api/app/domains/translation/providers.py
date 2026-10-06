"""Interchangeable translation providers.

- ``rule_based`` keeps local development free and deterministic for a curated
  phrase set.
- ``openai_compatible`` handles arbitrary text through a chat-completions API.
- ``azure_translator`` uses Microsoft Azure Translator for arbitrary ES/EN/SR
  text without changing the tutor provider.
"""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass

import httpx

from app.core.ai_client import (
    AIClientConfigurationError,
    AIClientError,
    AIClientUnavailableError,
    OpenAICompatibleChatClient,
)
from app.core.config import settings


class TranslationProviderError(RuntimeError):
    pass


class TranslationUnavailableError(TranslationProviderError):
    pass


@dataclass(slots=True)
class TranslationResult:
    translated_text: str
    learning_note: str | None = None
    exact_match: bool = True


def _normalize(text: str) -> str:
    value = unicodedata.normalize("NFKC", text).strip().casefold()
    value = re.sub(r"[¿?¡!.,;:]+$", "", value)
    value = re.sub(r"\s+", " ", value)
    return value


# Curated concept phrases used by the free local demo. Serbian output uses Latin script.
_PHRASES: tuple[dict[str, str], ...] = (
    {"es": "Hola", "en": "Hello", "sr": "Zdravo"},
    {"es": "Buenos días", "en": "Good morning", "sr": "Dobro jutro"},
    {"es": "Buenas tardes", "en": "Good afternoon", "sr": "Dobar dan"},
    {"es": "Buenas noches", "en": "Good night", "sr": "Laku noć"},
    {"es": "Gracias", "en": "Thank you", "sr": "Hvala"},
    {"es": "Por favor", "en": "Please", "sr": "Molim"},
    {"es": "Sí", "en": "Yes", "sr": "Da"},
    {"es": "No", "en": "No", "sr": "Ne"},
    {"es": "¿Cómo estás?", "en": "How are you?", "sr": "Kako si?"},
    {"es": "Estoy bien", "en": "I am fine", "sr": "Dobro sam"},
    {"es": "No entiendo", "en": "I don't understand", "sr": "Ne razumem"},
    {"es": "¿Puedes repetir?", "en": "Can you repeat?", "sr": "Možeš li da ponoviš?"},
    {"es": "Habla más despacio", "en": "Speak more slowly", "sr": "Govori sporije"},
    {"es": "Necesito ayuda", "en": "I need help", "sr": "Treba mi pomoć"},
    {"es": "¿Cuánto cuesta?", "en": "How much does it cost?", "sr": "Koliko košta?"},
    {"es": "¿Dónde está el baño?", "en": "Where is the bathroom?", "sr": "Gde je toalet?"},
    {"es": "¿Dónde está el aeropuerto?", "en": "Where is the airport?", "sr": "Gde je aerodrom?"},
    {"es": "Quiero aprender inglés", "en": "I want to learn English", "sr": "Želim da učim engleski"},
    {"es": "Quiero aprender español", "en": "I want to learn Spanish", "sr": "Želim da učim španski"},
    {"es": "Quiero aprender serbio", "en": "I want to learn Serbian", "sr": "Želim da učim srpski"},
    {"es": "Encantado de conocerte", "en": "Nice to meet you", "sr": "Drago mi je"},
    {"es": "Hasta luego", "en": "See you later", "sr": "Vidimo se kasnije"},
    {"es": "¿Hablas inglés?", "en": "Do you speak English?", "sr": "Govoriš li engleski?"},
    {"es": "Quiero una habitación", "en": "I want a room", "sr": "Želim sobu"},
    {"es": "Necesito un médico", "en": "I need a doctor", "sr": "Treba mi lekar"},
)

_SERBIAN_ALIASES: dict[str, str] = {
    _normalize("Здраво"): _normalize("Zdravo"),
    _normalize("Хвала"): _normalize("Hvala"),
    _normalize("Молим"): _normalize("Molim"),
    _normalize("Да"): _normalize("Da"),
    _normalize("Не"): _normalize("Ne"),
    _normalize("Не разумем"): _normalize("Ne razumem"),
    _normalize("Добро јутро"): _normalize("Dobro jutro"),
}


class RuleBasedTranslationProvider:
    async def translate(self, text: str, source: str, target: str) -> TranslationResult:
        normalized = _normalize(text)
        if source == "sr":
            normalized = _SERBIAN_ALIASES.get(normalized, normalized)

        for phrase in _PHRASES:
            if _normalize(phrase[source]) == normalized:
                return TranslationResult(
                    translated_text=phrase[target],
                    learning_note=self._learning_note(source, target),
                    exact_match=True,
                )

        name_match = self._translate_name_pattern(text, source, target)
        if name_match:
            return TranslationResult(
                translated_text=name_match,
                learning_note=self._learning_note(source, target),
                exact_match=True,
            )

        raise TranslationUnavailableError(
            "La traducción local gratuita reconoce un conjunto de frases de demostración. "
            "Configura TRANSLATION_PROVIDER=azure_translator u openai_compatible para traducir texto libre."
        )

    @staticmethod
    def _translate_name_pattern(text: str, source: str, target: str) -> str | None:
        patterns = {
            "es": re.compile(r"^\s*me llamo\s+(.+?)\s*[.!?]?\s*$", re.IGNORECASE),
            "en": re.compile(r"^\s*my name is\s+(.+?)\s*[.!?]?\s*$", re.IGNORECASE),
            "sr": re.compile(r"^\s*zovem se\s+(.+?)\s*[.!?]?\s*$", re.IGNORECASE),
        }
        match = patterns[source].match(text)
        if not match:
            return None
        name = match.group(1).strip()
        templates = {
            "es": f"Me llamo {name}",
            "en": f"My name is {name}",
            "sr": f"Zovem se {name}",
        }
        return templates[target]

    @staticmethod
    def _learning_note(source: str, target: str) -> str:
        names = {"es": "español", "en": "inglés", "sr": "serbio"}
        return f"Traducción de demostración {names[source]} → {names[target]}."


class AzureTranslatorProvider:
    """Arbitrary text translation using Microsoft Azure Translator REST v3."""

    @staticmethod
    def _contains_cyrillic(text: str) -> bool:
        return any("\u0400" <= char <= "\u04ff" for char in text)

    @classmethod
    def _source_code(cls, code: str, text: str) -> str:
        if code == "sr":
            return "sr-Cyrl" if cls._contains_cyrillic(text) else "sr-Latn"
        return code

    @staticmethod
    def _target_code(code: str) -> str:
        # LinguaAI uses Serbian Latin by default for consistency in the UI.
        return "sr-Latn" if code == "sr" else code

    async def translate(self, text: str, source: str, target: str) -> TranslationResult:
        api_key = settings.azure_translator_key.get_secret_value() if settings.azure_translator_key else ""
        if not api_key:
            raise TranslationProviderError(
                "AZURE_TRANSLATOR_KEY is missing for TRANSLATION_PROVIDER=azure_translator"
            )

        headers = {
            "Ocp-Apim-Subscription-Key": api_key,
            "Content-Type": "application/json",
        }
        if settings.azure_translator_region:
            headers["Ocp-Apim-Subscription-Region"] = settings.azure_translator_region

        endpoint = settings.azure_translator_endpoint.rstrip("/") + "/translate"
        params = {
            "api-version": "3.0",
            "from": self._source_code(source, text),
            "to": self._target_code(target),
        }

        try:
            async with httpx.AsyncClient(timeout=settings.ai_timeout_seconds) as client:
                response = await client.post(
                    endpoint,
                    params=params,
                    headers=headers,
                    json=[{"text": text}],
                )
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            if status in (401, 403):
                raise TranslationProviderError(
                    "Azure Translator rejected the configured credentials or quota"
                ) from exc
            raise TranslationProviderError("Azure Translator returned an HTTP error") from exc
        except httpx.HTTPError as exc:
            raise TranslationProviderError("Azure Translator could not be reached") from exc

        try:
            payload = response.json()
            translated = str(payload[0]["translations"][0]["text"]).strip()
            if not translated:
                raise ValueError("empty translation")
            return TranslationResult(
                translated_text=translated,
                learning_note=None,
                exact_match=True,
            )
        except (IndexError, KeyError, TypeError, ValueError) as exc:
            raise TranslationProviderError("Azure Translator returned an invalid response") from exc


class OpenAICompatibleTranslationProvider:
    async def translate(self, text: str, source: str, target: str) -> TranslationResult:
        names = {"es": "Spanish", "en": "English", "sr": "Serbian"}
        system_prompt = f"""
You are the translation engine inside LinguaAI Coach.
Translate from {names[source]} to {names[target]}.
Preserve meaning, register, names, numbers and formatting. Do not add facts.
For Serbian, use natural contemporary Serbian and keep the script choice natural to the input context; Latin script is acceptable by default.
Return ONLY valid JSON:
{{"translated_text":"...","learning_note":null}}
The learning_note is optional and, when useful, must be one concise note about a relevant expression or grammar point. Do not include pronunciation analysis.
""".strip()

        try:
            completion = await OpenAICompatibleChatClient().chat_completion(
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text},
                ],
                max_tokens=1000,
                temperature=0.15,
            )
        except AIClientConfigurationError as exc:
            raise TranslationProviderError(str(exc)) from exc
        except AIClientUnavailableError as exc:
            raise TranslationProviderError(str(exc)) from exc
        except AIClientError as exc:
            raise TranslationProviderError(str(exc)) from exc

        try:
            content = completion.content
            if content.startswith("```"):
                content = re.sub(r"^```(?:json)?\s*", "", content, flags=re.IGNORECASE)
                content = re.sub(r"\s*```$", "", content)
            payload = json.loads(content)
            translated = str(payload["translated_text"]).strip()
            note_value = payload.get("learning_note")
            note = str(note_value).strip() if note_value is not None else None
            if not translated:
                raise ValueError("empty translation")
            return TranslationResult(translated_text=translated, learning_note=note or None, exact_match=True)
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise TranslationProviderError("El proveedor de IA devolvió una traducción inválida.") from exc


def get_translation_provider():
    provider = settings.effective_translation_provider
    if provider == "azure_translator":
        return AzureTranslatorProvider()
    if provider == "openai_compatible":
        return OpenAICompatibleTranslationProvider()
    return RuleBasedTranslationProvider()
