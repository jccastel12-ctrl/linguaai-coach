import uuid

from fastapi import APIRouter, HTTPException, Query, status

from app.domains.auth.dependencies import CurrentUser, DbSession
from app.domains.billing import service as billing_service
from app.domains.tutor import service
from app.domains.tutor.schemas import (
    LearningMemoryRead,
    TutorExchange,
    TutorMessageRequest,
    TutorSessionCreate,
    TutorSessionDetail,
    TutorSessionRead,
    TutorStatsRead,
)

router = APIRouter(prefix="/tutor", tags=["tutor"])


@router.post("/sessions", response_model=TutorSessionRead, status_code=status.HTTP_201_CREATED)
async def create_tutor_session(data: TutorSessionCreate, current_user: CurrentUser, db: DbSession):
    try:
        return await service.create_session(db, current_user, data)
    except service.UnknownLanguageError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Unknown language: {exc}") from exc


@router.get("/sessions", response_model=list[TutorSessionRead])
async def my_tutor_sessions(
    current_user: CurrentUser,
    db: DbSession,
    limit: int = Query(default=20, ge=1, le=100),
):
    return await service.list_sessions(db, current_user, limit)


@router.get("/sessions/{session_id}", response_model=TutorSessionDetail)
async def tutor_session(session_id: uuid.UUID, current_user: CurrentUser, db: DbSession):
    try:
        return await service.get_session(db, current_user, session_id)
    except service.TutorSessionNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Tutor session not found") from exc


@router.post("/sessions/{session_id}/messages", response_model=TutorExchange)
async def tutor_message(
    session_id: uuid.UUID,
    data: TutorMessageRequest,
    current_user: CurrentUser,
    db: DbSession,
):
    try:
        await billing_service.check_feature_limit(db, current_user, "tutor_message")
        user_turn, assistant_turn = await service.send_message(db, current_user, session_id, data)
        await billing_service.record_usage(db, current_user, "tutor_message")
    except billing_service.PlanLimitExceededError as exc:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, detail=str(exc)) from exc
    except service.TutorSessionNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Tutor session not found") from exc
    except service.TutorProviderError as exc:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    return TutorExchange(session_id=session_id, user_turn=user_turn, assistant_turn=assistant_turn)


@router.get("/stats", response_model=TutorStatsRead)
async def tutor_stats(current_user: CurrentUser, db: DbSession):
    return await service.get_stats(db, current_user)


@router.get("/memory", response_model=list[LearningMemoryRead])
async def learning_memory(
    current_user: CurrentUser,
    db: DbSession,
    limit: int = Query(default=50, ge=1, le=100),
):
    return await service.list_memories(db, current_user, limit)
