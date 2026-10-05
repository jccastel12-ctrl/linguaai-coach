from app.domains.translation.providers import (
    AzureTranslatorProvider,
    OpenAICompatibleTranslationProvider,
    TranslationProviderError,
    TranslationUnavailableError,
    get_translation_provider,
)
from app.domains.translation.schemas import TranslationRequest, TranslationResponse


async def translate_text(data: TranslationRequest) -> TranslationResponse:
    provider = get_translation_provider()
    result = await provider.translate(data.text, data.source_language, data.target_language)

    if isinstance(provider, AzureTranslatorProvider):
        provider_name = "azure_translator"
    elif isinstance(provider, OpenAICompatibleTranslationProvider):
        provider_name = "openai_compatible"
    else:
        provider_name = "rule_based"

    return TranslationResponse(
        source_language=data.source_language,
        target_language=data.target_language,
        source_text=data.text,
        translated_text=result.translated_text,
        provider=provider_name,
        learning_note=result.learning_note,
        exact_match=result.exact_match,
    )


__all__ = [
    "TranslationProviderError",
    "TranslationUnavailableError",
    "translate_text",
]
