from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import math

from app.db.session import get_db
from app.core.deps import get_current_active_user
from app.models.auth import User
from app.schemas.customer import (
    CustomerCreate, CustomerUpdate, CustomerOut, CustomerListOut,
    CustomerDetailsCreate, CustomerDetailsOut,
    PaginatedResponse, MessageResponse,
)
from app.services import customer as svc

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("/stats")
async def customer_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return await svc.get_customer_stats(db, current_user.tenant_id)


@router.get("", response_model=PaginatedResponse)
async def list_customers(
    page:             int           = Query(1, ge=1),
    page_size:        int           = Query(20, ge=1, le=100),
    search:           Optional[str] = Query(None),
    status:           Optional[str] = Query(None),
    customer_type:    Optional[str] = Query(None),
    kyc_status:       Optional[str] = Query(None),
    assigned_user_id: Optional[int] = Query(None),
    branch_id:        Optional[int] = Query(None),
    tag:              Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    customers, total = await svc.get_customers(
        db, current_user.tenant_id, page, page_size,
        search, status, customer_type, kyc_status,
        assigned_user_id, branch_id, tag,
    )
    return PaginatedResponse(
        items=[CustomerListOut.model_validate(c) for c in customers],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total else 1,
    )


@router.post("", response_model=CustomerOut, status_code=201)
async def create_customer(
    data: CustomerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        customer = await svc.create_customer(db, current_user.tenant_id, data)
        return CustomerOut.model_validate(customer)
    except Exception as e:
        import traceback
        print(f"Error creating customer: {e}")
        print(traceback.format_exc())
        raise


@router.get("/{customer_id}", response_model=CustomerOut)
async def get_customer(
    customer_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    customer = await svc.get_customer(db, current_user.tenant_id, customer_id)
    return CustomerOut.model_validate(customer)


@router.patch("/{customer_id}", response_model=CustomerOut)
async def update_customer(
    data: CustomerUpdate,
    customer_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    customer = await svc.update_customer(db, current_user.tenant_id, customer_id, data)
    return CustomerOut.model_validate(customer)


@router.delete("/{customer_id}", response_model=MessageResponse)
async def delete_customer(
    customer_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    await svc.delete_customer(db, current_user.tenant_id, customer_id)
    return MessageResponse(message="Customer deleted.")


# ─── Customer Details ─────────────────────────────────────────────────────────

@router.put("/{customer_id}/details", response_model=CustomerDetailsOut)
async def upsert_customer_details(
    data: CustomerDetailsCreate,
    customer_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    details = await svc.update_customer_details(db, current_user.tenant_id, customer_id, data)
    return CustomerDetailsOut.model_validate(details)


# ─── KYC ─────────────────────────────────────────────────────────────────────

@router.patch("/{customer_id}/kyc", response_model=CustomerOut)
async def update_kyc(
    customer_id: int = Path(...),
    kyc_status: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    customer = await svc.update_kyc_status(db, current_user.tenant_id, customer_id, kyc_status)
    return CustomerOut.model_validate(customer)
