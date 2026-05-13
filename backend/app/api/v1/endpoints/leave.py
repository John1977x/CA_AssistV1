from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.deps import get_db, get_current_user
from app.core.security import decode_token
from app.models.auth import User, UserRole
from app.models.company_v2 import CompanyUser, CompanyRole
from sqlalchemy import select
from app.schemas.leave import (
    LeaveMasterCreate, LeaveMasterUpdate, LeaveMasterOut, PaginatedLeaveMasters,
)
from app.services import leave as leave_svc

router = APIRouter(prefix="/leave-master", tags=["leave-master"])
_bearer = HTTPBearer(auto_error=False)


def _get_jwt_role(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
) -> Optional[str]:
    """Extract role claim from JWT without a DB hit."""
    if not credentials:
        return None
    try:
        return decode_token(credentials.credentials).get("role")
    except Exception:
        return None


async def _resolve_role(db: AsyncSession, user: User) -> Optional[str]:
    """Return the user's role name, checking CompanyUser first then legacy UserRole."""
    if user.is_owner:
        return "OWNER"

    # Check V2 CompanyUser table — treat NULL is_deleted same as False
    result = await db.execute(
        select(CompanyRole.role_name)
        .select_from(CompanyUser)
        .join(CompanyRole, CompanyUser.role_id == CompanyRole.role_id)
        .where(CompanyUser.user_id == user.user_id, CompanyUser.is_deleted.isnot(True))
        .order_by(CompanyUser.created_at.desc())
        .limit(1)
    )
    role = result.scalar_one_or_none()
    if role:
        return role.upper()

    # Fall back to legacy UserRole table
    if user.role_id:
        lr = await db.execute(
            select(UserRole.role_code).where(UserRole.role_id == user.role_id)
        )
        code = lr.scalar_one_or_none()
        if code:
            return code.upper()

    return None


async def _require_staff(
    db: AsyncSession, user: User, jwt_role: Optional[str] = None,
) -> None:
    role = await _resolve_role(db, user)
    effective = role or (jwt_role.upper() if jwt_role else None)
    if effective not in ("OWNER", "MANAGER", "EMPLOYEE"):
        raise HTTPException(status_code=403, detail="Only firm staff can manage leave masters.")


@router.get("", response_model=PaginatedLeaveMasters)
async def list_leave_masters(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    calendar_year: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = await leave_svc.get_leave_masters(
        db, current_user.tenant_id, page, page_size, calendar_year,
    )
    return PaginatedLeaveMasters(
        items=items, total=total, page=page, page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.post("", response_model=LeaveMasterOut, status_code=201)
async def create_leave_master(
    data: LeaveMasterCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    jwt_role: Optional[str] = Depends(_get_jwt_role),
):
    await _require_staff(db, current_user, jwt_role)
    return await leave_svc.create_leave_master(db, current_user.tenant_id, data)


@router.get("/{leave_master_id}", response_model=LeaveMasterOut)
async def get_leave_master(
    leave_master_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await leave_svc.get_leave_master(db, current_user.tenant_id, leave_master_id)


@router.patch("/{leave_master_id}", response_model=LeaveMasterOut)
async def update_leave_master(
    leave_master_id: int,
    data: LeaveMasterUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    jwt_role: Optional[str] = Depends(_get_jwt_role),
):
    await _require_staff(db, current_user, jwt_role)
    return await leave_svc.update_leave_master(db, current_user.tenant_id, leave_master_id, data)


@router.delete("/{leave_master_id}", status_code=204)
async def delete_leave_master(
    leave_master_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    jwt_role: Optional[str] = Depends(_get_jwt_role),
):
    await _require_staff(db, current_user, jwt_role)
    await leave_svc.delete_leave_master(db, current_user.tenant_id, leave_master_id)
