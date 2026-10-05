import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domains.languages.service import get_language
from app.domains.tutor.models import LearningMemory, TutorSession, TutorTurn
from app.domains.tutor.providers import TutorContext, TutorProviderError, get_tutor_provider
from app.domains.tutor.schemas import TutorMessageRequest, TutorSessionCreate
from app.domains.users.models import User


class TutorSessionNotFoundError(LookupError):
    pass


class UnknownLanguageError(ValueError):
    pass


async def create_session(db: AsyncSession, user: User, data: TutorSessionCreate) -> TutorSession:
    code = data.target_language_code.lower()
    if await get_language(db, code) is None:
        raise UnknownLanguageError(code)
    session = TutorSession(
        user_id=user.id,
        target_language_code=code,
        cefr_level=data.cefr_level,
        personality=data.personality,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def list_sessions(db: AsyncSession, user: User, limit: int = 20) -> list[TutorSession]:
    result = await db.scalars(
        select(TutorSession)
        .where(TutorSession.user_id == user.id)
        .order_by(desc(TutorSession.updated_at))
        .limit(limit)
    )
    return list(result.unique().all())


async def get_session(db: AsyncSession, user: User, session_id: uuid.UUID) -> TutorSession:
    result = await db.execute(
        select(TutorSession)
        .options(selectinload(TutorSession.turns))
        .where(TutorSession.id == session_id, TutorSession.user_id == user.id)
    )
    session = result.scalar_one_or_none()
    if session is None:
        raise TutorSessionNotFoundError
    return session


async def send_message(
    db: AsyncSession,
    user: User,
    session_id: uuid.UUID,
    data: TutorMessageRequest,
) -> tuple[TutorTurn, TutorTurn]:
    session = await get_session(db, user, session_id)
    history = [(turn.role, turn.content) for turn in session.turns[-10:]]
    native_language = user.profile.native_language_code if user.profile else None
    context = TutorContext(
        target_language=session.target_language_code,
        native_language=native_language,
        cefr_level=session.cefr_level,
        personality=session.personality,
        history=history,
    )

    provider = get_tutor_provider()
    result = await provider.generate(data.text, context)

    user_turn = TutorTurn(session_id=session.id, role="user", content=data.text.strip())
    assistant_turn = TutorTurn(
        session_id=session.id,
        role="assistant",
        content=result.reply,
        corrected_text=result.corrected_text,
        explanation=result.explanation,
        translation=result.translation,
        feedback_meta={
            "errors": [
                {"category": error.category, "key": error.key, "note": error.note}
                for error in result.errors
            ]
        }
        if result.errors
        else None,
    )
    db.add_all([user_turn, assistant_turn])

    if session.title is None:
        clean_title = " ".join(data.text.strip().split())
        session.title = clean_title[:117] + "..." if len(clean_title) > 120 else clean_title
    session.updated_at = datetime.now(timezone.utc)

    for error in result.errors:
        await _remember_error(
            db,
            user_id=user.id,
            language_code=session.target_language_code,
            category=error.category if error.category in {"grammar", "vocabulary", "pronunciation", "usage"} else "usage",
            memory_key=error.key,
            note=error.note,
            example=data.text.strip(),
        )

    await db.commit()
    await db.refresh(user_turn)
    await db.refresh(assistant_turn)
    return user_turn, assistant_turn


async def _remember_error(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    language_code: str,
    category: str,
    memory_key: str,
    note: str,
    example: str,
) -> None:
    memory_key = memory_key[:120]
    memory = await db.scalar(
        select(LearningMemory).where(
            LearningMemory.user_id == user_id,
            LearningMemory.language_code == language_code,
            LearningMemory.category == category,
            LearningMemory.memory_key == memory_key,
        )
    )
    if memory is None:
        memory = LearningMemory(
            user_id=user_id,
            language_code=language_code,
            category=category,
            memory_key=memory_key,
            note=note,
            last_example=example,
        )
        db.add(memory)
    else:
        memory.occurrence_count += 1
        memory.note = note
        memory.last_example = example


async def get_stats(db: AsyncSession, user: User) -> dict[str, int | str | None]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)

    total_sessions = await db.scalar(
        select(func.count()).select_from(TutorSession).where(TutorSession.user_id == user.id)
    ) or 0
    total_user_messages = await db.scalar(
        select(func.count())
        .select_from(TutorTurn)
        .join(TutorSession, TutorTurn.session_id == TutorSession.id)
        .where(TutorSession.user_id == user.id, TutorTurn.role == "user")
    ) or 0
    total_corrections = await db.scalar(
        select(func.count())
        .select_from(TutorTurn)
        .join(TutorSession, TutorTurn.session_id == TutorSession.id)
        .where(
            TutorSession.user_id == user.id,
            TutorTurn.role == "assistant",
            TutorTurn.corrected_text.is_not(None),
        )
    ) or 0
    memory_patterns = await db.scalar(
        select(func.count()).select_from(LearningMemory).where(LearningMemory.user_id == user.id)
    ) or 0
    repeated_patterns = await db.scalar(
        select(func.count())
        .select_from(LearningMemory)
        .where(LearningMemory.user_id == user.id, LearningMemory.occurrence_count > 1)
    ) or 0
    sessions_last_7_days = await db.scalar(
        select(func.count())
        .select_from(TutorSession)
        .where(TutorSession.user_id == user.id, TutorSession.created_at >= cutoff)
    ) or 0

    occurrence_sum = func.sum(LearningMemory.occurrence_count).label("occurrences")
    category_result = await db.execute(
        select(LearningMemory.category, occurrence_sum)
        .where(LearningMemory.user_id == user.id)
        .group_by(LearningMemory.category)
        .order_by(occurrence_sum.desc())
        .limit(1)
    )
    category_row = category_result.first()

    pattern_result = await db.execute(
        select(LearningMemory.memory_key)
        .where(LearningMemory.user_id == user.id)
        .order_by(desc(LearningMemory.occurrence_count), desc(LearningMemory.updated_at))
        .limit(1)
    )
    pattern_row = pattern_result.first()

    return {
        "total_sessions": int(total_sessions),
        "total_user_messages": int(total_user_messages),
        "total_corrections": int(total_corrections),
        "memory_patterns": int(memory_patterns),
        "repeated_patterns": int(repeated_patterns),
        "sessions_last_7_days": int(sessions_last_7_days),
        "most_frequent_category": category_row[0] if category_row else None,
        "most_frequent_pattern": pattern_row[0] if pattern_row else None,
    }


async def list_memories(db: AsyncSession, user: User, limit: int = 50) -> list[LearningMemory]:
    result = await db.scalars(
        select(LearningMemory)
        .where(LearningMemory.user_id == user.id)
        .order_by(desc(LearningMemory.occurrence_count), desc(LearningMemory.updated_at))
        .limit(limit)
    )
    return list(result.all())


__all__ = [
    "TutorProviderError",
    "TutorSessionNotFoundError",
    "UnknownLanguageError",
    "create_session",
    "get_session",
    "get_stats",
    "list_memories",
    "list_sessions",
    "send_message",
]
