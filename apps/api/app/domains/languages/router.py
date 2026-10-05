from fastapi import APIRouter, HTTPException, status

from app.domains.auth.dependencies import DbSession
from app.domains.languages import service
from app.domains.languages.schemas import LanguageRead

router = APIRouter(prefix="/languages", tags=["languages"])


@router.get("", response_model=list[LanguageRead])
async def list_languages(db: DbSession) -> list:
    return await service.list_languages(db)


@router.get("/{code}", response_model=LanguageRead)
async def get_language(code: str, db: DbSession):
    language = await service.get_language(db, code)
    if language is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Language not found")
    return language
