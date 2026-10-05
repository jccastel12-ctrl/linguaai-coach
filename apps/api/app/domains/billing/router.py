from fastapi import APIRouter

from app.domains.auth.dependencies import CurrentUser, DbSession
from app.domains.billing import service
from app.domains.billing.schemas import BillingOverview, PaymentCapabilities, PlanRead, UpgradeRequestResponse

router = APIRouter(prefix="/billing", tags=["billing"])


@router.get("/plans", response_model=list[PlanRead])
async def plans():
    return service.list_plans()


@router.get("/payment-capabilities", response_model=PaymentCapabilities)
async def payment_capabilities():
    return service.payment_capabilities()


@router.get("/me", response_model=BillingOverview)
async def my_billing(current_user: CurrentUser, db: DbSession):
    return await service.get_overview(db, current_user)


@router.post("/me/request-upgrade", response_model=UpgradeRequestResponse)
async def request_upgrade(current_user: CurrentUser, db: DbSession):
    return await service.request_upgrade(db, current_user)
