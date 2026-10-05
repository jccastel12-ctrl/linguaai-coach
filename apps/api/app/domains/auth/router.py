from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.domains.auth import service
from app.domains.auth.dependencies import CurrentUser, DbSession
from app.domains.auth.email import send_password_reset_email, send_verification_email
from app.domains.auth.schemas import (
    ChangePasswordRequest,
    LoginRequest,
    MessageResponse,
    OneTimeTokenRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    RegisterRequest,
    TokenResponse,
)
from app.domains.users import service as users_service
from app.domains.users.schemas import UserRead

router = APIRouter(prefix="/auth", tags=["auth"])

_invalid_credentials = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Incorrect email or password",
    headers={"WWW-Authenticate": "Bearer"},
)


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, db: DbSession):
    if await users_service.get_user_by_email(db, data.email) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    user = await users_service.create_user(db, email=data.email, password=data.password, full_name=data.full_name)
    raw_token = await service.create_account_token(db, user, purpose="email_verification", lifetime_minutes=24 * 60)
    await send_verification_email(user.email, raw_token)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: DbSession) -> TokenResponse:
    user = await service.authenticate(db, data.email, data.password)
    if user is None:
        raise _invalid_credentials
    return service.issue_token(user)


@router.post("/token", response_model=TokenResponse, include_in_schema=True)
async def token(form: Annotated[OAuth2PasswordRequestForm, Depends()], db: DbSession) -> TokenResponse:
    """OAuth2 password flow (used by the Swagger UI 'Authorize' button)."""
    user = await service.authenticate(db, form.username, form.password)
    if user is None:
        raise _invalid_credentials
    return service.issue_token(user)


@router.get("/me", response_model=UserRead)
async def me(current_user: CurrentUser) -> UserRead:
    return current_user


@router.post("/password/change", response_model=MessageResponse)
async def change_password(data: ChangePasswordRequest, current_user: CurrentUser, db: DbSession) -> MessageResponse:
    if not await service.change_password(db, current_user, data.current_password, data.new_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")
    return MessageResponse(message="Password updated. Sign in again on other sessions.")


@router.post("/password-reset/request", response_model=MessageResponse, status_code=status.HTTP_202_ACCEPTED)
async def request_password_reset(data: PasswordResetRequest, db: DbSession) -> MessageResponse:
    # Always return the same response to prevent account enumeration.
    user = await users_service.get_user_by_email(db, data.email)
    if user is not None and user.is_active:
        raw_token = await service.create_account_token(db, user, purpose="password_reset", lifetime_minutes=60)
        await send_password_reset_email(user.email, raw_token)
    return MessageResponse(message="If the account exists, password reset instructions were sent.")


@router.post("/password-reset/confirm", response_model=MessageResponse)
async def confirm_password_reset(data: PasswordResetConfirm, db: DbSession) -> MessageResponse:
    if not await service.reset_password(db, data.token, data.new_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset link")
    return MessageResponse(message="Password updated successfully.")


@router.post("/email-verification/request", response_model=MessageResponse, status_code=status.HTTP_202_ACCEPTED)
async def request_email_verification(current_user: CurrentUser, db: DbSession) -> MessageResponse:
    if current_user.email_verified_at is None:
        raw_token = await service.create_account_token(
            db, current_user, purpose="email_verification", lifetime_minutes=24 * 60
        )
        await send_verification_email(current_user.email, raw_token)
    return MessageResponse(message="If verification is pending, a new link was sent.")


@router.post("/email-verification/confirm", response_model=UserRead)
async def confirm_email_verification(data: OneTimeTokenRequest, db: DbSession) -> UserRead:
    user = await service.verify_email(db, data.token)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired verification link")
    return user
