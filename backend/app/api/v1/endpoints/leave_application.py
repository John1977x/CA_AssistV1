from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.core.deps import get_db, get_current_user
from app.core.security import decode_token
from app.models.auth import User, UserRole
from app.models.company_v2 import CompanyUser, CompanyRole
from sqlalchemy import select
from app.schemas.leave import (
    LeaveApplicationCreate, LeaveApplicationUpdate,
    LeaveApplicationOut, PaginatedLeaveApplications, ApproverOut,
)
from app.services import leave as leave_svc

router = APIRouter(prefix="/leave-application", tags=["leave-application"])
_bearer = HTTPBearer(auto_error=False)


def _get_jwt_role(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
) -> Optional[str]:
    if not credentials:
        return None
    try:
        return decode_token(credentials.credentials).get("role")
    except Exception:
        return None


async def _resolve_role(db: AsyncSession, user: User) -> Optional[str]:
    if user.is_owner:
        return "OWNER"
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
    if user.role_id:
        lr = await db.execute(
            select(UserRole.role_code).where(UserRole.role_id == user.role_id)
        )
        code = lr.scalar_one_or_none()
        if code:
            return code.upper()
    return None


async def _get_effective_role(
    db: AsyncSession, user: User, jwt_role: Optional[str],
) -> Optional[str]:
    role = await _resolve_role(db, user)
    return role or (jwt_role.upper() if jwt_role else None)


@router.get("/approvers", response_model=List[ApproverOut])
async def list_approvers(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await leave_svc.get_approvers(db, current_user.tenant_id)


@router.get("", response_model=PaginatedLeaveApplications)
async def list_leave_applications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    jwt_role: Optional[str] = Depends(_get_jwt_role),
):
    role = await _get_effective_role(db, current_user, jwt_role)
    # Employees see only their own; managers/owners see all
    employee_filter = None if role in ("OWNER", "MANAGER") else current_user.user_id
    items, total = await leave_svc.get_leave_applications(
        db, current_user.tenant_id, page, page_size, employee_filter, status,
    )
    return PaginatedLeaveApplications(
        items=items, total=total, page=page, page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.post("", response_model=LeaveApplicationOut, status_code=201)
async def create_leave_application(
    data: LeaveApplicationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await leave_svc.create_leave_application(
        db, current_user.tenant_id, current_user.user_id, data,
    )


@router.get("/{leave_application_id}", response_model=LeaveApplicationOut)
async def get_leave_application(
    leave_application_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await leave_svc.get_leave_application(
        db, current_user.tenant_id, leave_application_id,
    )


@router.patch("/{leave_application_id}", response_model=LeaveApplicationOut)
async def update_leave_application(
    leave_application_id: int,
    data: LeaveApplicationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    jwt_role: Optional[str] = Depends(_get_jwt_role),
):
    app = await leave_svc.get_leave_application(
        db, current_user.tenant_id, leave_application_id,
    )
    role = await _get_effective_role(db, current_user, jwt_role)
    is_own = app.employee_id == current_user.user_id
    is_manager = role in ("OWNER", "MANAGER")

    # Employees can only edit their own PENDING applications (non-status fields)
    if not is_manager and not is_own:
        raise HTTPException(status_code=403, detail="Not authorised.")
    if not is_manager and is_own and app.status != "PENDING":
        raise HTTPException(status_code=403, detail="Cannot edit a non-pending application.")
    if not is_manager:
        data.status = None
        data.approval_notes = None

    return await leave_svc.update_leave_application(
        db, current_user.tenant_id, leave_application_id, data,
    )


@router.delete("/{leave_application_id}", status_code=204)
async def delete_leave_application(
    leave_application_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    jwt_role: Optional[str] = Depends(_get_jwt_role),
):
    app = await leave_svc.get_leave_application(
        db, current_user.tenant_id, leave_application_id,
    )
    role = await _get_effective_role(db, current_user, jwt_role)
    if role not in ("OWNER", "MANAGER") and app.employee_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not authorised.")
    await leave_svc.delete_leave_application(
        db, current_user.tenant_id, leave_application_id,
    )
