"""Proveedores intercambiables para el tutor conversacional.

`rule_based` permite probar el producto sin pagar una API externa.
`openai_compatible` usa cualquier endpoint compatible con /chat/completions.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

from app.core.ai_client import (
    AIClientConfigurationError,
    AIClientError,
    AIClientUnavailableError,
    OpenAICompatibleChatClient,
)
from app.core.config import settings


@dataclass(slots=True)
class LearningError:
    category: str
    key: str
    note: str


@dataclass(slots=True)
class TutorResult:
    reply: str
    corrected_text: str | None = None
    explanation: str | None = None
    translation: str | None = None
    errors: list[LearningError] = field(default_factory=list)


@dataclass(slots=True)
class TutorContext:
    target_language: str
    native_language: str | None
    cefr_level: str
    personality: str
    history: list[tuple[str, str]]


class TutorProviderError(RuntimeError):
    pass


class RuleBasedTutorProvider:
    """Fallback gratuito y determinista para desarrollo y demostración."""

    async def generate(self, text: str, context: TutorContext) -> TutorResult:
        stripped = text.strip()
        lower = stripped.lower()

        if context.target_language == "en":
            age = re.search(r"\bi have\s+(\d{1,3})\s+years(?:\s+old)?\b", lower)
            if age:
                corrected = f"I am {age.group(1)} years old."
                return TutorResult(
                    reply="Good correction. Now tell me where you are from.",
                    corrected_text=corrected,
                    explanation=self._explain(
                        context.native_language,
                        "En inglés la edad se expresa con el verbo 'to be', no con 'have'.",
                        "In English, age is expressed with 'to be', not 'have'.",
                        "U engleskom se godine izražavaju glagolom 'to be', ne sa 'have'.",
                    ),
                    translation=None,
                    errors=[LearningError("grammar", "age_with_be", "Use 'to be' to express age in English.")],
                )
            if "i am agree" in lower:
                corrected = re.sub(r"\bi am agree\b", "I agree", stripped, flags=re.IGNORECASE)
                return TutorResult(
                    reply="Exactly. What do you agree with?",
                    corrected_text=corrected,
                    explanation=self._explain(
                        context.native_language,
                        "'Agree' es un verbo: se dice 'I agree', sin 'am'.",
                        "'Agree' is a verb, so say 'I agree' without 'am'.",
                        "'Agree' je glagol, zato se kaže 'I agree' bez 'am'.",
                    ),
                    translation=None,
                    errors=[LearningError("grammar", "agree_without_be", "Use 'I agree', not 'I am agree'.")],
                )

        if context.target_language == "es" and "yo sabo" in lower:
            corrected = re.sub(r"\byo sabo\b", "yo sé", stripped, flags=re.IGNORECASE)
            return TutorResult(
                reply="Muy bien. ¿Qué otras cosas sabes hacer?",
                corrected_text=corrected,
                explanation=self._explain(
                    context.native_language,
                    "El presente de 'saber' en primera persona es irregular: 'yo sé'.",
                    "The first-person present of 'saber' is irregular: 'yo sé'.",
                    "Prvo lice prezenta glagola 'saber' je nepravilno: 'yo sé'.",
                ),
                translation=None,
                errors=[LearningError("grammar", "saber_first_person", "Use 'yo sé' for first-person present of saber.")],
            )

        if context.target_language == "sr" and re.search(r"\bja sam\s+\d{1,3}\s+godina\b", lower):
            corrected = re.sub(r"\bja sam\s+(\d{1,3})\s+godina\b", r"Imam \1 godina", stripped, flags=re.IGNORECASE)
            return TutorResult(
                reply="Odlično. Reci mi odakle si.",
                corrected_text=corrected,
                explanation=self._explain(
                    context.native_language,
                    "En serbio la edad se expresa con 'imam' (tengo), no con 'ja sam'.",
                    "In Serbian, age is expressed with 'imam' (I have), not 'ja sam'.",
                    "U srpskom se godine izražavaju sa 'imam', a ne sa 'ja sam'.",
                ),
                translation=None,
                errors=[LearningError("grammar", "serbian_age_imam", "Use 'imam' to express age in Serbian.")],
            )

        replies = {
            "en": "Great. Tell me a little more about that.",
            "es": "Muy bien. Cuéntame un poco más sobre eso.",
            "sr": "Odlično. Reci mi nešto više o tome.",
        }
        return TutorResult(
            reply=replies.get(context.target_language, "Tell me a little more."),
            translation=self._translate_reply(context.native_language, context.target_language),
        )

    @staticmethod
    def _explain(native: str | None, es: str, en: str, sr: str) -> str:
        return {"es": es, "en": en, "sr": sr}.get(native or "", en)

    @staticmethod
    def _translate_reply(native: str | None, target: str) -> str | None:
        if not native or native == target:
            return None
        translations = {
            ("es", "en"): "Muy bien. Cuéntame un poco más sobre eso.",
            ("sr", "en"): "Odlično. Reci mi nešto više o tome.",
            ("en", "es"): "Great. Tell me a little more about that.",
            ("sr", "es"): "Odlično. Reci mi nešto više o tome.",
            ("es", "sr"): "Muy bien. Cuéntame un poco más sobre eso.",
            ("en", "sr"): "Great. Tell me a little more about that.",
        }
        return translations.get((native, target))


class OpenAICompatibleTutorProvider:
    async def generate(self, text: str, context: TutorContext) -> TutorResult:
        api_key = settings.ai_api_key.get_secret_value() if settings.ai_api_key else ""
        if not api_key or not settings.ai_model:
            raise TutorProviderError("AI provider is configured but AI_API_KEY/AI_MODEL is missing")

        system_prompt = f"""
You are a language tutor inside LinguaAI Coach.
Target language: {context.target_language}.
Student native/support language: {context.native_language or 'unknown'}.
CEFR level: {context.cefr_level}.
Tutor personality: {context.personality}.

Goals:
- Keep the conversation primarily in the target language and suitable for the CEFR level.
- Correct the student's sentence only when there is a meaningful grammar, vocabulary or usage error.
- Give a short pedagogical explanation in the student's support language when known.
- Keep the reply concise and continue the conversation with a natural question when appropriate.
- Do not claim pronunciation analysis: this is text-only mode.

Return ONLY a valid JSON object with this shape:
{{
  "reply": "string",
  "corrected_text": null,
  "explanation": null,
  "translation": null,
  "errors": [{{"category":"grammar|vocabulary|usage","key":"stable_short_key","note":"short note"}}]
}}
""".strip()

        messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
        for role, content in context.history[-10:]:
            messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": text})

        try:
            completion = await OpenAICompatibleChatClient().chat_completion(
                messages,
                max_tokens=500,
                temperature=0.35,
            )
        except AIClientConfigurationError as exc:
            raise TutorProviderError(str(exc)) from exc
        except AIClientUnavailableError as exc:
            raise TutorProviderError(str(exc)) from exc
        except AIClientError as exc:
            raise TutorProviderError(str(exc)) from exc

        try:
            content = completion.content
            payload = self._decode_json(content)
            errors = [
                LearningError(
                    category=item.get("category", "usage"),
                    key=str(item.get("key") or "general_usage")[:120],
                    note=str(item.get("note") or "Review this usage pattern."),
                )
                for item in payload.get("errors", [])[:5]
                if isinstance(item, dict)
            ]
            reply = str(payload["reply"]).strip()
            if not reply:
                raise ValueError("empty reply")
            return TutorResult(
                reply=reply,
                corrected_text=self._optional_text(payload.get("corrected_text")),
                explanation=self._optional_text(payload.get("explanation")),
                translation=self._optional_text(payload.get("translation")),
                errors=errors,
            )
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise TutorProviderError("The AI provider returned an invalid tutor response") from exc

    @staticmethod
    def _decode_json(content: str) -> dict:
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r"\s*```$", "", cleaned)
        data = json.loads(cleaned)
        if not isinstance(data, dict):
            raise ValueError("Tutor response must be a JSON object")
        return data

    @staticmethod
    def _optional_text(value: object) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None


def get_tutor_provider():
    if settings.ai_provider == "openai_compatible":
        return OpenAICompatibleTutorProvider()
    return RuleBasedTutorProvider()
