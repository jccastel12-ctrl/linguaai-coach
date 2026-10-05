from fastapi import APIRouter, HTTPException, status

from app.domains.auth.dependencies import CurrentUser, DbSession
from app.domains.users import service
from app.domains.users.schemas import (
    StudentProfileRead,
    StudentProfileUpdate,
    UserLanguageRead,
    UserLanguageUpsert,
    UserRead,
    UserUpdate,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
async def read_me(current_user: CurrentUser):
    return current_user


@router.patch("/me", response_model=UserRead)
async def update_me(data: UserUpdate, current_user: CurrentUser, db: DbSession):
    return await service.update_user(db, current_user, data)


@router.patch("/me/profile", response_model=StudentProfileRead)
async def update_my_profile(data: StudentProfileUpdate, current_user: CurrentUser, db: DbSession):
    try:
        return await service.update_profile(db, current_user, data)
    except service.UnknownLanguageError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Unknown language: {exc}") from exc


@router.put("/me/languages", response_model=UserLanguageRead)
async def upsert_my_language(data: UserLanguageUpsert, current_user: CurrentUser, db: DbSession):
    try:
        return await service.upsert_learning_language(db, current_user, data)
    except service.UnknownLanguageError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Unknown language: {exc}") from exc
