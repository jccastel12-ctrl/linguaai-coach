import re
import unicodedata
from dataclasses import dataclass
from difflib import SequenceMatcher


CYRILLIC_TO_LATIN = str.maketrans({
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "ђ": "dj", "е": "e", "ж": "z",
    "з": "z", "и": "i", "ј": "j", "к": "k", "л": "l", "љ": "lj", "м": "m", "н": "n",
    "њ": "nj", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "ћ": "c", "у": "u",
    "ф": "f", "х": "h", "ц": "c", "ч": "c", "џ": "dz", "ш": "s",
    "А": "a", "Б": "b", "В": "v", "Г": "g", "Д": "d", "Ђ": "dj", "Е": "e", "Ж": "z",
    "З": "z", "И": "i", "Ј": "j", "К": "k", "Л": "l", "Љ": "lj", "М": "m", "Н": "n",
    "Њ": "nj", "О": "o", "П": "p", "Р": "r", "С": "s", "Т": "t", "Ћ": "c", "У": "u",
    "Ф": "f", "Х": "h", "Ц": "c", "Ч": "c", "Џ": "dz", "Ш": "s",
})


@dataclass(frozen=True)
class PronunciationScore:
    overall_score: int
    word_accuracy: int
    transcript_similarity: int
    missing_words: list[str]
    extra_words: list[str]


def normalize_text(text: str, language_code: str) -> str:
    value = text.strip().lower()
    if language_code == "sr":
        value = value.translate(CYRILLIC_TO_LATIN)
        value = (
            value.replace("dž", "dz")
            .replace("đ", "dj")
            .replace("č", "c")
            .replace("ć", "c")
            .replace("š", "s")
            .replace("ž", "z")
        )
    value = "".join(ch for ch in unicodedata.normalize("NFKD", value) if not unicodedata.combining(ch))
    value = re.sub(r"[^a-z0-9\s']", " ", value)
    return " ".join(value.split())


def _word_diff(expected: str, recognized: str) -> tuple[list[str], list[str], int]:
    expected_tokens = expected.split()
    recognized_tokens = recognized.split()
    matcher = SequenceMatcher(None, expected_tokens, recognized_tokens)
    matched = sum(block.size for block in matcher.get_matching_blocks())
    missing: list[str] = []
    extra: list[str] = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag in {"delete", "replace"}:
            missing.extend(expected_tokens[i1:i2])
        if tag in {"insert", "replace"}:
            extra.extend(recognized_tokens[j1:j2])
    denominator = max(len(expected_tokens), len(recognized_tokens), 1)
    accuracy = round(100 * matched / denominator)
    return missing, extra, accuracy


def score_transcript(expected_text: str, recognized_text: str, language_code: str) -> PronunciationScore:
    expected = normalize_text(expected_text, language_code)
    recognized = normalize_text(recognized_text, language_code)
    similarity = round(SequenceMatcher(None, expected, recognized).ratio() * 100)
    missing, extra, word_accuracy = _word_diff(expected, recognized)
    overall = round(similarity * 0.55 + word_accuracy * 0.45)
    return PronunciationScore(
        overall_score=overall,
        word_accuracy=word_accuracy,
        transcript_similarity=similarity,
        missing_words=missing,
        extra_words=extra,
    )
