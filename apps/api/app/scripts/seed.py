"""Idempotent development seed: sample published lessons for es/en/sr.

Usage: python -m app.scripts.seed
Languages themselves are inserted by migration 001.
"""

from sqlalchemy import select

from app.core.config import settings
from app.core.database import SessionLocal
from app.models import Language, Lesson

SAMPLE_LESSONS = [
    {
        "language_code": "es",
        "slug": "saludos-basicos",
        "title": "Saludos básicos",
        "cefr_level": "A1",
        "content": {"version": 1, "vocabulary": ["hola", "buenos días", "adiós"]},
    },
    {
        "language_code": "en",
        "slug": "basic-greetings",
        "title": "Basic greetings",
        "cefr_level": "A1",
        "content": {"version": 1, "vocabulary": ["hello", "good morning", "goodbye"]},
    },
    {
        "language_code": "sr",
        "slug": "osnovni-pozdravi",
        "title": "Osnovni pozdravi / Основни поздрави",
        "cefr_level": "A1",
        "content": {
            "version": 1,
            "vocabulary": ["zdravo / здраво", "dobro jutro / добро јутро", "doviđenja / довиђења"],
        },
    },
]


def main() -> None:
    if settings.is_production:
        raise SystemExit("Refusing to seed sample data in staging/production")
    with SessionLocal() as db:
        created = 0
        for data in SAMPLE_LESSONS:
            if db.get(Language, data["language_code"]) is None:
                raise SystemExit(f"Language {data['language_code']} missing - run migrations first")
            exists = db.scalar(
                select(Lesson).where(Lesson.language_code == data["language_code"], Lesson.slug == data["slug"])
            )
            if exists is None:
                db.add(Lesson(**data, is_published=True, estimated_minutes=10))
                created += 1
        db.commit()
    print(f"Seed complete: {created} lesson(s) created")


if __name__ == "__main__":
    main()
