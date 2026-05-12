from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.deps import get_db, get_current_user
from app.models.auth import User
from app.schemas.register import (
    RegisterCreate, RegisterUpdate, RegisterOut,
    PaginatedRegisters, RegisterStats,
)
from app.services import register as register_svc

router = APIRouter(prefix="/register", tags=["register"])


@router.get("/stats", response_model=RegisterStats)
async def stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await register_svc.get_stats(db, current_user.tenant_id)


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
    items, total = await register_svc.get_registers(
        db, current_user.tenant_id, page, page_size, in_out_ward, doc_type, search
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
    await register_svc.delete_register(db, current_user.tenant_id, register_id)
