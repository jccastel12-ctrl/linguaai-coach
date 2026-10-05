from fastapi import APIRouter, HTTPException, Query, status

from app.core.constants import CEFR_LEVELS
from app.domains.auth.dependencies import CurrentUser, DbSession
from app.domains.billing import service as billing_service
from app.domains.pronunciation import service
from app.domains.pronunciation.schemas import (
    PronunciationEvaluateRequest,
    PronunciationEvaluation,
    PronunciationExercise,
    PronunciationStats,
)

router = APIRouter(prefix="/pronunciation", tags=["pronunciation"])


@router.get("/exercises", response_model=list[PronunciationExercise])
async def list_exercises(
    current_user: CurrentUser,
    language_code: str = Query(min_length=2, max_length=8),
    cefr_level: str = Query(default="A1"),
):
    if cefr_level.upper() not in CEFR_LEVELS:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid CEFR level")
    rows = service.exercises(language_code, cefr_level)
    if not rows:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="No pronunciation exercises available")
    return rows


@router.post("/evaluate", response_model=PronunciationEvaluation, status_code=status.HTTP_201_CREATED)
async def evaluate_pronunciation(
    data: PronunciationEvaluateRequest,
    current_user: CurrentUser,
    db: DbSession,
):
    if data.language_code.lower() not in {"es", "en", "sr"}:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Unsupported language")
    try:
        await billing_service.check_feature_limit(db, current_user, "pronunciation")
        attempt, missing, extra = await service.evaluate(db, current_user, data)
        await billing_service.record_usage(db, current_user, "pronunciation")
    except billing_service.PlanLimitExceededError as exc:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, detail=str(exc)) from exc
    result = PronunciationEvaluation.model_validate(attempt)
    return result.model_copy(update={"missing_words": missing, "extra_words": extra})


@router.get("/stats", response_model=PronunciationStats)
async def pronunciation_stats(current_user: CurrentUser, db: DbSession):
    return await service.stats(db, current_user)


@router.get("/attempts", response_model=list[PronunciationEvaluation])
async def pronunciation_attempts(current_user: CurrentUser, db: DbSession, limit: int = Query(default=10, ge=1, le=50)):
    attempts = await service.recent_attempts(db, current_user, limit)
    return [PronunciationEvaluation.model_validate(item) for item in attempts]
