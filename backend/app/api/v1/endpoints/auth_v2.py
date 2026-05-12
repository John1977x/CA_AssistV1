"""
Authentication Endpoints for Multi-Company, Multi-Role Architecture
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.auth_v2 import (
    OwnerRegisterRequest, OwnerRegisterResponse,
    LoginRequest, LoginResponse,
    TokenRefreshRequest, TokenRefreshResponse,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ChangeCompanyBranchRequest, ChangeCompanyBranchResponse,
)
from app.services.auth_v2 import (
    register_owner, login_user, change_company_branch,
)
from app.core.security import (
    create_access_token, decode_token, verify_password, hash_password,
)
from app.core.config import settings
from app.core.deps import get_current_user
from app.models.auth import User
from datetime import datetime, timezone

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ─── Owner Registration ──────────────────────────────────────────────────────

@router.post("/register-owner", response_model=OwnerRegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_owner_endpoint(
    request: OwnerRegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new owner and create their first company
    
    - **first_name**: Owner's first name
    - **last_name**: Owner's last name
    - **email**: Owner's email (must be unique)
    - **phone**: Owner's phone number
    - **password**: Password (min 8 chars, must have uppercase, lowercase, digit)
    - **company_name**: Name of the company
    - **company_code**: Unique company code
    """
    return await register_owner(db, request)


# ─── Login ───────────────────────────────────────────────────────────────────

@router.post("/login", response_model=LoginResponse)
async def login_endpoint(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Login with email and password
    
    Returns access token, refresh token, user profile, and company info
    """
    return await login_user(db, request)


# ─── Token Refresh ──────────────────────────────────────────────────────────

@router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh_token_endpoint(
    request: TokenRefreshRequest,
):
    """
    Refresh access token using refresh token
    """
    try:
        payload = decode_token(request.refresh_token)
        user_id = payload.get("user_id")
        email = payload.get("email")
        
        if not user_id or not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Create new access token
        access_token = create_access_token(
            subject=user_id,
            extra={"email": email}
        )
        
        return TokenRefreshResponse(
            access_token=access_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


# ─── Get Current User ───────────────────────────────────────────────────────

@router.get("/me")
async def get_current_user_endpoint(
    current_user: User = Depends(get_current_user),
):
    """
    Get current user profile
    """
    return {
        "user_id": current_user.user_id,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "display_name": current_user.display_name,
        "phone": current_user.phone,
        "avatar_url": current_user.avatar_url,
        "is_owner": current_user.is_owner,
        "is_two_factor_enabled": current_user.is_two_factor_enabled,
        "status": current_user.status,
    }


# ─── Logout ──────────────────────────────────────────────────────────────────

@router.post("/logout")
async def logout_endpoint(
    current_user: User = Depends(get_current_user),
):
    """
    Logout (stateless - just return success)
    """
    return {"message": "Logged out successfully"}


# ─── Change Password ────────────────────────────────────────────────────────

@router.post("/change-password")
async def change_password_endpoint(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Change password for current user
    """
    # Verify current password
    if not verify_password(request.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Verify new passwords match
    if request.new_password != request.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New passwords do not match"
        )
    
    # Update password
    current_user.password_hash = hash_password(request.new_password)
    current_user.password_changed_at = datetime.now(timezone.utc)
    
    await db.commit()
    
    return {"message": "Password changed successfully"}


# ─── Forgot Password ────────────────────────────────────────────────────────

@router.post("/forgot-password")
async def forgot_password_endpoint(
    request: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Request password reset
    """
    from sqlalchemy import select
    from app.models.auth import User
    
    # Find user by email
    result = await db.execute(
        select(User).where(User.email == request.email)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        # Don't reveal if email exists
        return {"message": "If email exists, password reset link will be sent"}
    
    # Generate reset token
    reset_token = create_access_token(
        subject=user.user_id,
        extra={"email": user.email, "type": "reset"},
    )

    # In production, send email with reset link
    # For now, just return success

    return {"message": "Password reset link sent to email"}


# ─── Reset Password ────────────────────────────────────────────────────────

@router.post("/reset-password")
async def reset_password_endpoint(
    request: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Reset password with token
    """
    try:
        payload = decode_token(request.token)
        user_id = payload.get("user_id")
        token_type = payload.get("type")
        
        if token_type != "reset":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token"
            )
        
        from sqlalchemy import select
        from app.models.auth import User
        
        # Get user
        result = await db.execute(
            select(User).where(User.user_id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not found"
            )
        
        # Update password
        user.password_hash = hash_password(request.new_password)
        user.password_changed_at = datetime.now(timezone.utc)
        
        await db.commit()
        
        return {"message": "Password reset successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )


# ─── Change Company/Branch ──────────────────────────────────────────────────

@router.post("/change-company-branch", response_model=ChangeCompanyBranchResponse)
async def change_company_branch_endpoint(
    request: ChangeCompanyBranchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Change user's company and branch (owner only)
    
    - **company_id**: ID of the company to switch to
    - **branch_id**: ID of the branch (optional)
    """
    # Call service
    company_info = await change_company_branch(
        db,
        current_user.user_id,
        request.company_id,
        request.branch_id
    )
    
    return ChangeCompanyBranchResponse(
        message="Company and branch changed successfully",
        company=company_info
    )

