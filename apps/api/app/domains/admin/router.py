import uuid

from fastapi import APIRouter, HTTPException, Query, status

from app.domains.admin import service
from app.domains.admin.schemas import (
    AdminAuditEventRead,
    AdminOverview,
    AdminSubscriptionUpdate,
    AdminUserList,
    AdminUserRead,
    AdminUserStatusUpdate,
)
from app.domains.auth.dependencies import AdminUser, DbSession

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/overview", response_model=AdminOverview)
async def admin_overview(admin: AdminUser, db: DbSession):
    return await service.overview(db)


@router.get("/users", response_model=AdminUserList)
async def admin_users(
    admin: AdminUser,
    db: DbSession,
    search: str | None = Query(default=None, max_length=120),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    upgrade_requests_only: bool = False,
):
    return await service.list_users(
        db,
        search=search,
        limit=limit,
        offset=offset,
        upgrade_requests_only=upgrade_requests_only,
    )


@router.patch("/users/{user_id}/subscription", response_model=AdminUserRead)
async def update_subscription(user_id: uuid.UUID, data: AdminSubscriptionUpdate, admin: AdminUser, db: DbSession):
    updated = await service.set_subscription(db, actor=admin, target_user_id=user_id, data=data)
    if updated is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
    return updated


@router.patch("/users/{user_id}/active", response_model=AdminUserRead)
async def update_user_active(user_id: uuid.UUID, data: AdminUserStatusUpdate, admin: AdminUser, db: DbSession):
    try:
        target = await service.set_user_active(
            db,
            actor=admin,
            target_user_id=user_id,
            is_active=data.is_active,
            note=data.note,
        )
    except ValueError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    if target is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
    result = await service.list_users(db, search=target.email, limit=1, offset=0)
    return result["items"][0]


@router.get("/audit", response_model=list[AdminAuditEventRead])
async def audit_log(admin: AdminUser, db: DbSession, limit: int = Query(default=25, ge=1, le=100)):
    return await service.list_audit(db, limit=limit)
