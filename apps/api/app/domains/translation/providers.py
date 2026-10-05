"""Interchangeable translation providers.

The rule-based provider keeps local development free and deterministic for a
curated phrase set. The OpenAI-compatible provider handles arbitrary text when
AI_PROVIDER=openai_compatible is configured.
"""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass

import httpx

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

# Accept both common Serbian Latin and Cyrillic demo inputs.
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
            "Configura AI_PROVIDER=openai_compatible para traducir texto libre."
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


class OpenAICompatibleTranslationProvider:
    async def translate(self, text: str, source: str, target: str) -> TranslationResult:
        api_key = settings.ai_api_key.get_secret_value() if settings.ai_api_key else ""
        if not api_key or not settings.ai_model:
            raise TranslationProviderError("AI_API_KEY/AI_MODEL is missing for the configured AI provider")

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
            async with httpx.AsyncClient(timeout=settings.ai_timeout_seconds) as client:
                response = await client.post(
                    settings.ai_base_url.rstrip("/") + "/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                    json={
                        "model": settings.ai_model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": text},
                        ],
                        "temperature": 0.15,
                        "max_tokens": 1000,
                    },
                )
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise TranslationProviderError("The configured AI provider could not be reached") from exc

        try:
            content = response.json()["choices"][0]["message"]["content"].strip()
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
            raise TranslationProviderError("The AI provider returned an invalid translation response") from exc


def get_translation_provider():
    if settings.ai_provider == "openai_compatible":
        return OpenAICompatibleTranslationProvider()
    return RuleBasedTranslationProvider()
