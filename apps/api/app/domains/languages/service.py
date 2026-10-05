from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.languages.models import Language


async def list_languages(db: AsyncSession, *, active_only: bool = True) -> list[Language]:
    stmt = select(Language).order_by(Language.code)
    if active_only:
        stmt = stmt.where(Language.is_active.is_(True))
    return list(await db.scalars(stmt))


async def get_language(db: AsyncSession, code: str) -> Language | None:
    return await db.get(Language, code.lower())
