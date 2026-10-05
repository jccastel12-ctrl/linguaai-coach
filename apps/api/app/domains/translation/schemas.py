from typing import Literal

from pydantic import BaseModel, Field, model_validator

LanguageCode = Literal["es", "en", "sr"]


class TranslationRequest(BaseModel):
    text: str = Field(min_length=1, max_length=5000)
    source_language: LanguageCode
    target_language: LanguageCode

    @model_validator(mode="after")
    def validate_language_pair(self) -> "TranslationRequest":
        if self.source_language == self.target_language:
            raise ValueError("Source and target languages must be different")
        self.text = self.text.strip()
        if not self.text:
            raise ValueError("Text cannot be empty")
        return self


class TranslationResponse(BaseModel):
    source_language: LanguageCode
    target_language: LanguageCode
    source_text: str
    translated_text: str
    provider: Literal["rule_based", "openai_compatible", "azure_translator"]
    learning_note: str | None = None
    exact_match: bool = True
