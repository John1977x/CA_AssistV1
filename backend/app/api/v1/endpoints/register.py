from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.core.deps import get_db, get_current_user
from app.models.auth import User
from app.models.company_v2 import CompanyUser, CompanyRole
from app.models.customer import Customer
from app.schemas.register import (
    RegisterCreate, RegisterUpdate, RegisterOut,
    PaginatedRegisters, RegisterStats,
)
from app.services import register as register_svc

router = APIRouter(prefix="/register", tags=["register"])


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


async def _customer_id_for_user(db: AsyncSession, email: str) -> Optional[int]:
    """Resolve a client user's customer_id by matching email (same pattern as tickets)."""
    result = await db.execute(select(Customer).where(Customer.email == email))
    customer = result.scalar_one_or_none()
    return customer.customer_id if customer else None


async def _role_filters(db: AsyncSession, current_user: User):
    """Return (filter_employee_id, filter_client_id) based on the user's role."""
    role = await _get_role(db, current_user.user_id)
    if role == "EMPLOYEE":
        return current_user.user_id, None
    if role == "CLIENT":
        cid = await _customer_id_for_user(db, current_user.email)
        return None, cid
    return None, None  # OWNER / MANAGER see everything


@router.get("/stats", response_model=RegisterStats)
async def stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    emp_id, cli_id = await _role_filters(db, current_user)
    return await register_svc.get_stats(
        db, current_user.tenant_id,
        filter_employee_id=emp_id,
        filter_client_id=cli_id,
    )


@router.get("", response_model=PaginatedRegisters)
async def list_entries(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    in_out_ward: Optional[str] = None,
    doc_type: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    emp_id, cli_id = await _role_filters(db, current_user)
    items, total = await register_svc.get_registers(
        db, current_user.tenant_id, page, page_size,
        in_out_ward, doc_type, search,
        filter_employee_id=emp_id,
        filter_client_id=cli_id,
    )
    return PaginatedRegisters(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.post("", response_model=RegisterOut, status_code=201)
async def create_entry(
    data: RegisterCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await register_svc.create_register(db, current_user.tenant_id, data)


@router.get("/{register_id}", response_model=RegisterOut)
async def get_entry(
    register_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await register_svc.get_register(db, current_user.tenant_id, register_id)


@router.patch("/{register_id}", response_model=RegisterOut)
async def update_entry(
    register_id: int,
    data: RegisterUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await register_svc.update_register(db, current_user.tenant_id, register_id, data)


@router.delete("/{register_id}", status_code=204)
async def delete_entry(
    register_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role = await _get_role(db, current_user.user_id)
    if role not in ("OWNER", "MANAGER", None):
        raise HTTPException(status_code=403, detail="Only owners and managers can delete register entries.")
    await register_svc.delete_register(db, current_user.tenant_id, register_id)
