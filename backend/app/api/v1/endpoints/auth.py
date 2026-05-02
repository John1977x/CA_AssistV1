from fastapi import APIRouter, Depends, HTTPException, Request, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.session import get_db
from app.core.deps import get_current_active_user, get_client_ip
from app.core.config import settings
from app.models.auth import User
from app.schemas.auth import (
    Token, LoginRequest, RegisterTenantRequest,
    ChangePasswordRequest, ForgotPasswordRequest, ResetPasswordRequest,
    TokenRefresh, Enable2FAResponse, Verify2FARequest,
    MessageResponse, UserOut, TenantOut,
)
from app.services import auth as auth_svc

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=MessageResponse, status_code=201)
async def register(
    data: RegisterTenantRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Register a new CA firm and create owner account."""
    await auth_svc.register_tenant(db, data)
    return MessageResponse(message="Registration successful! Please check your email and log in.")


@router.post("/login", response_model=Token)
async def login(
    data: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Login with email + password (+ optional TOTP code)."""
    ip = get_client_ip(request)
    ua = request.headers.get("user-agent", "")
    user, access_token, refresh_token = await auth_svc.authenticate_user(db, data, ip, ua)

    from app.core.config import settings
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserOut.model_validate(user),
    )


@router.post("/refresh", response_model=dict)
async def refresh_token(
    body: TokenRefresh,
    db: AsyncSession = Depends(get_db),
):
    """Refresh access token using refresh token."""
    access, refresh = await auth_svc.refresh_access_token(db, body.refresh_token)
    return {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


@router.post("/logout", response_model=MessageResponse)
async def logout(current_user: User = Depends(get_current_active_user)):
    """Logout (client should discard tokens)."""
    # Stateless JWT — client discards tokens; add to blacklist if needed
    return MessageResponse(message="Logged out successfully.")


@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_active_user)):
    """Get current logged-in user profile."""
    return UserOut.model_validate(current_user)


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    data: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    await auth_svc.change_password(db, current_user, data)
    return MessageResponse(message="Password changed successfully.")


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    await auth_svc.forgot_password(db, data.email)
    return MessageResponse(message="If this email is registered, you will receive a password reset link.")


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    await auth_svc.reset_password(db, data.token, data.new_password)
    return MessageResponse(message="Password reset successfully. Please login.")


# ─── 2FA ────────────────────────────────────────────────────────────────────

@router.post("/2fa/enable", response_model=Enable2FAResponse)
async def enable_2fa(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Initiate 2FA setup — returns QR code and backup secret."""
    qr, secret = await auth_svc.enable_2fa(db, current_user)
    return Enable2FAResponse(qr_code=qr, secret=secret)


@router.post("/2fa/confirm", response_model=MessageResponse)
async def confirm_2fa(
    data: Verify2FARequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Confirm 2FA setup by verifying TOTP code."""
    await auth_svc.confirm_2fa(db, current_user, data.totp_code)
    return MessageResponse(message="Two-factor authentication enabled successfully.")


@router.post("/2fa/disable", response_model=MessageResponse)
async def disable_2fa(
    data: Verify2FARequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Disable 2FA by confirming current TOTP code."""
    await auth_svc.disable_2fa(db, current_user, data.totp_code)
    return MessageResponse(message="Two-factor authentication disabled.")
