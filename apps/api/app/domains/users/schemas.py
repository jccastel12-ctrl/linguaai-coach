import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.constants import CefrLevel


class StudentProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    display_name: str | None
    native_language_code: str | None
    timezone: str
    daily_goal_minutes: int
    bio: str | None


class StudentProfileUpdate(BaseModel):
    display_name: str | None = Field(default=None, max_length=80)
    native_language_code: str | None = Field(default=None, min_length=2, max_length=8)
    timezone: str | None = Field(default=None, max_length=64)
    daily_goal_minutes: int | None = Field(default=None, ge=1, le=480)
    bio: str | None = Field(default=None, max_length=1000)


class UserLanguageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    language_code: str
    cefr_level: CefrLevel
    is_primary: bool


class UserLanguageUpsert(BaseModel):
    language_code: str = Field(min_length=2, max_length=8)
    cefr_level: CefrLevel = "A1"
    is_primary: bool = False


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    full_name: str | None
    is_active: bool
    is_superuser: bool
    email_verified_at: datetime | None
    created_at: datetime
    profile: StudentProfileRead | None = None
    languages: list[UserLanguageRead] = []


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, max_length=120)
