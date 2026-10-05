import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.domains.billing.schemas import PlanTier, SubscriptionStatus


class AdminUsageSummary(BaseModel):
    tutor_message: int = 0
    translation: int = 0
    pronunciation: int = 0


class AdminOverview(BaseModel):
    total_users: int
    active_users: int
    pro_users: int
    pending_upgrade_requests: int
    new_users_last_7_days: int
    usage_today: AdminUsageSummary
    payment_provider: str
    checkout_enabled: bool


class AdminUserRead(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str | None
    is_active: bool
    is_superuser: bool
    created_at: datetime
    plan_tier: PlanTier
    subscription_status: SubscriptionStatus
    requested_plan: PlanTier | None
    payment_provider: str | None


class AdminUserList(BaseModel):
    items: list[AdminUserRead]
    total: int
    limit: int
    offset: int


class AdminSubscriptionUpdate(BaseModel):
    plan_tier: PlanTier
    status: SubscriptionStatus = "active"
    note: str | None = Field(default=None, max_length=500)


class AdminUserStatusUpdate(BaseModel):
    is_active: bool
    note: str | None = Field(default=None, max_length=500)


class AdminAuditEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    actor_user_id: uuid.UUID | None
    target_user_id: uuid.UUID
    action: str
    old_plan: str | None
    new_plan: str | None
    note: str | None
    created_at: datetime
