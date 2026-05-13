from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.deps import get_db, get_current_user
from app.models.auth import User
from app.models.company_v2 import CompanyUser, CompanyRole
from sqlalchemy import select
from app.schemas.leave import (
    LeaveMasterCreate, LeaveMasterUpdate, LeaveMasterOut, PaginatedLeaveMasters,
)
from app.services import leave as leave_svc

router = APIRouter(prefix="/leave-master", tags=["leave-master"])


async def _get_role(db: AsyncSession, user_id: int) -> Optional[str]:
    result = await db.execute(
        select(CompanyRole.role_name)
        .select_from(CompanyUser)
        .join(CompanyRole, CompanyUser.role_id == CompanyRole.role_id)
        .where(CompanyUser.user_id == user_id, CompanyUser.is_deleted == False)
        .order_by(CompanyUser.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def _require_owner_or_manager(db: AsyncSession, user: User) -> None:
    role = await _get_role(db, user.user_id)
    if role not in ("OWNER", "MANAGER"):
        raise HTTPException(status_code=403, detail="Only owners and managers can manage leave masters.")


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
):
    await _require_owner_or_manager(db, current_user)
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
):
    await _require_owner_or_manager(db, current_user)
    return await leave_svc.update_leave_master(db, current_user.tenant_id, leave_master_id, data)


@router.delete("/{leave_master_id}", status_code=204)
async def delete_leave_master(
    leave_master_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await _require_owner_or_manager(db, current_user)
    await leave_svc.delete_leave_master(db, current_user.tenant_id, leave_master_id)
