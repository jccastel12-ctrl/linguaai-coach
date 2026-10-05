from datetime import datetime
from typing import Literal

from pydantic import BaseModel

PlanTier = Literal["basic", "pro"]
SubscriptionStatus = Literal["active", "canceled", "past_due"]
FeatureKey = Literal["tutor_message", "translation", "pronunciation"]


class PlanLimits(BaseModel):
    tutor_messages_per_day: int
    translations_per_day: int
    pronunciation_attempts_per_day: int


class PlanRead(BaseModel):
    id: PlanTier
    name: str
    tagline: str
    audience: str
    limits: PlanLimits
    benefits: list[str]
    payment_enabled: bool = False


class FeatureUsageRead(BaseModel):
    feature: FeatureKey
    label: str
    used: int
    limit: int
    remaining: int


class BillingOverview(BaseModel):
    plan: PlanRead
    status: SubscriptionStatus
    requested_plan: PlanTier | None
    usage: list[FeatureUsageRead]
    resets_at: datetime
    payment_enabled: bool = False


class UpgradeRequestResponse(BaseModel):
    requested_plan: PlanTier
    message: str


class PaymentCapabilities(BaseModel):
    provider: str
    checkout_enabled: bool
    webhooks_enabled: bool
    note: str
