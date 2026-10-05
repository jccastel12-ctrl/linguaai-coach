from fastapi import APIRouter, HTTPException, status

from app.domains.auth.dependencies import CurrentUser, DbSession
from app.domains.billing import service as billing_service
from app.domains.translation import service
from app.domains.translation.schemas import TranslationRequest, TranslationResponse

router = APIRouter(prefix="/translate", tags=["translation"])


@router.post("", response_model=TranslationResponse)
async def translate_text(data: TranslationRequest, current_user: CurrentUser, db: DbSession):
    try:
        await billing_service.check_feature_limit(db, current_user, "translation")
        result = await service.translate_text(data)
        await billing_service.record_usage(db, current_user, "translation")
        return result
    except billing_service.PlanLimitExceededError as exc:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, detail=str(exc)) from exc
    except service.TranslationUnavailableError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except service.TranslationProviderError as exc:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
