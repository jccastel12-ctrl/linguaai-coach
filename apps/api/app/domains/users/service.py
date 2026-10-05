import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.domains.billing.models import Subscription
from app.domains.languages.service import get_language
from app.domains.users.models import StudentProfile, User, UserLanguage
from app.domains.users.schemas import StudentProfileUpdate, UserLanguageUpsert, UserUpdate


class UnknownLanguageError(ValueError):
    pass


def normalize_email(email: str) -> str:
    return email.strip().lower()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    return await db.scalar(select(User).where(User.email == normalize_email(email)))


async def get_user(db: AsyncSession, user_id: uuid.UUID) -> User | None:
    return await db.get(User, user_id)


async def create_user(db: AsyncSession, *, email: str, password: str, full_name: str | None = None) -> User:
    user = User(email=normalize_email(email), hashed_password=hash_password(password), full_name=full_name)
    user.profile = StudentProfile()
    db.add(user)
    await db.flush()
    db.add(Subscription(user_id=user.id, plan_tier="basic", status="active"))
    await db.commit()
    await db.refresh(user)
    return user


async def update_user(db: AsyncSession, user: User, data: UserUpdate) -> User:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    await db.commit()
    await db.refresh(user)
    return user


async def update_profile(db: AsyncSession, user: User, data: StudentProfileUpdate) -> StudentProfile:
    profile = user.profile or StudentProfile(user_id=user.id)
    changes = data.model_dump(exclude_unset=True)
    code = changes.get("native_language_code")
    if code is not None:
        if await get_language(db, code) is None:
            raise UnknownLanguageError(code)
        changes["native_language_code"] = code.lower()
    for field, value in changes.items():
        setattr(profile, field, value)
    if user.profile is None:
        user.profile = profile
    await db.commit()
    await db.refresh(profile)
    return profile


async def upsert_learning_language(db: AsyncSession, user: User, data: UserLanguageUpsert) -> UserLanguage:
    code = data.language_code.lower()
    if await get_language(db, code) is None:
        raise UnknownLanguageError(code)
    entry = next((ul for ul in user.languages if ul.language_code == code), None)
    if entry is None:
        entry = UserLanguage(language_code=code)
        user.languages.append(entry)
    entry.cefr_level = data.cefr_level
    if data.is_primary:
        for ul in user.languages:
            ul.is_primary = False
    entry.is_primary = data.is_primary
    await db.commit()
    await db.refresh(entry)
    return entry
