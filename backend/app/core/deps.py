from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError
from typing import Optional
import time

from app.db.session import get_db
from app.models.auth import User, Tenant
from app.core.security import decode_token
from app.core.config import settings

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not credentials:
        raise credentials_exception

    try:
        payload = decode_token(credentials.credentials)
        user_id: int = int(payload.get("sub"))
        token_type: str = payload.get("type")
        if token_type != "access":
            raise credentials_exception
    except (JWTError, ValueError, TypeError):
        raise credentials_exception

    result = await db.execute(
        select(User).where(
            User.user_id == user_id,
            User.is_deleted == False,
            User.status == "ACTIVE",
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        raise credentials_exception

    # Check if account is locked
    from datetime import datetime, timezone
    if user.locked_until and user.locked_until > datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is temporarily locked. Please try again later.",
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is not active.",
        )
    return current_user


async def get_current_tenant(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Tenant:
    result = await db.execute(
        select(Tenant).where(
            Tenant.tenant_id == current_user.tenant_id,
            Tenant.is_deleted == False,
        )
    )
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found.",
        )
    if tenant.status == "SUSPENDED":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been suspended. Please contact support.",
        )
    return tenant


class RequirePermission:
    """Dependency factory for permission-based access control."""
    def __init__(self, module: str, action: str = "read"):
        self.module = module
        self.action = action

    async def __call__(self, current_user: User = Depends(get_current_active_user)):
        from app.models.auth import UserRole
        # Owners bypass all permission checks
        if current_user.is_owner:
            return current_user

        role = current_user.role
        if not role:
            raise HTTPException(status_code=403, detail="No role assigned.")

        perms = role.permissions_json or {}
        module_perms = perms.get(self.module, {})

        if not module_perms.get(self.action, False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You don't have permission to {self.action} {self.module}.",
            )
        return current_user


def require_owner(current_user: User = Depends(get_current_active_user)) -> User:
    if not current_user.is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the firm owner can perform this action.",
        )
    return current_user


def require_can_manage_users(current_user: User = Depends(get_current_active_user)) -> User:
    if not current_user.is_owner and not (current_user.role and current_user.role.can_manage_users):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to manage users.",
        )
    return current_user


def get_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "unknown"
