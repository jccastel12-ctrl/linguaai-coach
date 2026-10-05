from app.domains.translation.providers import (
    TranslationProviderError,
    TranslationUnavailableError,
    get_translation_provider,
)
from app.domains.translation.schemas import TranslationRequest, TranslationResponse


async def translate_text(data: TranslationRequest) -> TranslationResponse:
    provider = get_translation_provider()
    result = await provider.translate(data.text, data.source_language, data.target_language)
    return TranslationResponse(
        source_language=data.source_language,
        target_language=data.target_language,
        source_text=data.text,
        translated_text=result.translated_text,
        provider="openai_compatible" if provider.__class__.__name__.startswith("OpenAI") else "rule_based",
        learning_note=result.learning_note,
        exact_match=result.exact_match,
    )


__all__ = [
    "TranslationProviderError",
    "TranslationUnavailableError",
    "translate_text",
]
