from datetime import UTC, datetime, timedelta
import hashlib
import secrets

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.domains.auth.models import AccountToken
from app.domains.auth.schemas import TokenResponse
from app.domains.users.models import User
from app.domains.users.service import get_user_by_email

# Pre-computed hash used to keep timing constant when the email does not exist.
_DUMMY_HASH = hash_password("timing-attack-mitigation-dummy")


async def authenticate(db: AsyncSession, email: str, password: str) -> User | None:
    user = await get_user_by_email(db, email)
    if user is None:
        verify_password(password, _DUMMY_HASH)
        return None
    if not verify_password(password, user.hashed_password) or not user.is_active:
        return None
    return user


def issue_token(user: User) -> TokenResponse:
    return TokenResponse(
        access_token=create_access_token(str(user.id), extra={"ver": user.auth_version}),
        expires_in=settings.access_token_expire_minutes * 60,
    )


def _hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def _aware(dt: datetime) -> datetime:
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=UTC)


async def create_account_token(
    db: AsyncSession,
    user: User,
    *,
    purpose: str,
    lifetime_minutes: int,
) -> str:
    raw_token = secrets.token_urlsafe(32)
    token = AccountToken(
        user_id=user.id,
        token_hash=_hash_token(raw_token),
        purpose=purpose,
        expires_at=datetime.now(UTC) + timedelta(minutes=lifetime_minutes),
    )
    db.add(token)
    await db.commit()
    return raw_token


async def consume_account_token(db: AsyncSession, raw_token: str, purpose: str) -> tuple[AccountToken, User] | None:
    token = await db.scalar(
        select(AccountToken).where(
            AccountToken.token_hash == _hash_token(raw_token),
            AccountToken.purpose == purpose,
            AccountToken.used_at.is_(None),
        )
    )
    if token is None or _aware(token.expires_at) < datetime.now(UTC):
        return None
    user = await db.get(User, token.user_id)
    if user is None or not user.is_active:
        return None
    token.used_at = datetime.now(UTC)
    return token, user


async def change_password(db: AsyncSession, user: User, current_password: str, new_password: str) -> bool:
    if not verify_password(current_password, user.hashed_password):
        return False
    user.hashed_password = hash_password(new_password)
    user.auth_version += 1
    await db.commit()
    return True


async def reset_password(db: AsyncSession, raw_token: str, new_password: str) -> bool:
    consumed = await consume_account_token(db, raw_token, "password_reset")
    if consumed is None:
        return False
    _token, user = consumed
    user.hashed_password = hash_password(new_password)
    user.auth_version += 1
    await db.commit()
    return True


async def verify_email(db: AsyncSession, raw_token: str) -> User | None:
    consumed = await consume_account_token(db, raw_token, "email_verification")
    if consumed is None:
        return None
    _token, user = consumed
    if user.email_verified_at is None:
        user.email_verified_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(user)
    return user
