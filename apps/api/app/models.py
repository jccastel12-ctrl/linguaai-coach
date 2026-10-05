"""Import every ORM model so Base.metadata is complete (used by Alembic and tests)."""

from app.core.database import Base
from app.domains.auth.models import AccountToken
from app.domains.billing.models import BillingAuditEvent, Subscription, UsageEvent
from app.domains.languages.models import Language
from app.domains.lessons.models import Lesson, LessonProgress
from app.domains.pronunciation.models import PronunciationAttempt
from app.domains.tutor.models import LearningMemory, TutorSession, TutorTurn
from app.domains.users.models import StudentProfile, User, UserLanguage

__all__ = [
    "Base",
    "AccountToken",
    "BillingAuditEvent",
    "Language",
    "Subscription",
    "UsageEvent",
    "Lesson",
    "LessonProgress",
    "LearningMemory",
    "PronunciationAttempt",
    "StudentProfile",
    "TutorSession",
    "TutorTurn",
    "User",
    "UserLanguage",
]
