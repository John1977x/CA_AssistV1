from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, or_, and_
from fastapi import HTTPException
from datetime import datetime, timezone, date as date_type
from typing import Optional, List, Tuple
import re

from app.models.customer import Customer, CustomerDetails
from app.schemas.customer import (
    CustomerCreate, CustomerUpdate,
    CustomerDetailsCreate,
)


# ─── Helpers ─────────────────────────────────────────────────────────────────

async def _generate_customer_code(db: AsyncSession, tenant_id: int) -> str:
    result = await db.execute(
        select(func.count(Customer.customer_id)).where(
            Customer.tenant_id == tenant_id,
            Customer.is_deleted == False,
        )
    )
    count = result.scalar() or 0
    return f"CLT-{str(count + 1).zfill(4)}"


# ─── Customer CRUD ───────────────────────────────────────────────────────────

async def get_customers(
    db: AsyncSession,
    tenant_id: int,
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None,
    status: Optional[str] = None,
    customer_type: Optional[str] = None,
    kyc_status: Optional[str] = None,
    assigned_user_id: Optional[int] = None,
    branch_id: Optional[int] = None,
    tag: Optional[str] = None,
) -> Tuple[List[Customer], int]:
    query = select(Customer).where(
        Customer.tenant_id == tenant_id,
        Customer.is_deleted == False,
    )

    if search:
        query = query.where(
            or_(
                Customer.display_name.ilike(f"%{search}%"),
                Customer.pan.ilike(f"%{search}%"),
                Customer.gstin.ilike(f"%{search}%"),
                Customer.email.ilike(f"%{search}%"),
                Customer.phone.ilike(f"%{search}%"),
                Customer.customer_code.ilike(f"%{search}%"),
            )
        )
    if status:
        query = query.where(Customer.status == status)
    if customer_type:
        query = query.where(Customer.customer_type == customer_type)
    if kyc_status:
        query = query.where(Customer.kyc_status == kyc_status)
    if assigned_user_id:
        query = query.where(Customer.assigned_user_id == assigned_user_id)
    if branch_id:
        query = query.where(Customer.branch_id == branch_id)
    if tag:
        query = query.where(Customer.tags.contains([tag]))

    count_result = await db.execute(
        select(func.count()).select_from(query.subquery())
    )
    total = count_result.scalar()

    query = query.offset((page - 1) * page_size).limit(page_size).order_by(Customer.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all(), total


async def get_customer(db: AsyncSession, tenant_id: int, customer_id: int) -> Customer:
    result = await db.execute(
        select(Customer).where(
            Customer.customer_id == customer_id,
            Customer.tenant_id == tenant_id,
            Customer.is_deleted == False,
        )
    )
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found.")
    return customer


async def create_customer(db: AsyncSession, tenant_id: int, data: CustomerCreate) -> Customer:
    # Check PAN uniqueness within tenant
    if data.pan:
        existing = await db.execute(
            select(Customer).where(
                Customer.tenant_id == tenant_id,
                Customer.pan == data.pan.upper(),
                Customer.is_deleted == False,
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail=f"A customer with PAN {data.pan.upper()} already exists.")

    # Check GSTIN uniqueness within tenant
    if data.gstin:
        existing = await db.execute(
            select(Customer).where(
                Customer.tenant_id == tenant_id,
                Customer.gstin == data.gstin.upper(),
                Customer.is_deleted == False,
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail=f"A customer with GSTIN {data.gstin.upper()} already exists.")

    code = await _generate_customer_code(db, tenant_id)
    customer_data = data.model_dump()

    # Normalize PAN / GSTIN
    if customer_data.get("pan"):
        customer_data["pan"] = customer_data["pan"].upper()
    if customer_data.get("gstin"):
        customer_data["gstin"] = customer_data["gstin"].upper()

    customer = Customer(
        tenant_id=tenant_id,
        customer_code=code,
        **customer_data,
    )
    db.add(customer)
    await db.flush()

    # Create empty details record
    details = CustomerDetails(customer_id=customer.customer_id)
    db.add(details)
    await db.commit()
    await db.refresh(customer)
    return customer


async def update_customer(
    db: AsyncSession, tenant_id: int, customer_id: int, data: CustomerUpdate
) -> Customer:
    customer = await get_customer(db, tenant_id, customer_id)
    update_data = data.model_dump(exclude_unset=True)

    if "pan" in update_data and update_data["pan"]:
        update_data["pan"] = update_data["pan"].upper()
        existing = await db.execute(
            select(Customer).where(
                Customer.tenant_id == tenant_id,
                Customer.pan == update_data["pan"],
                Customer.customer_id != customer_id,
                Customer.is_deleted == False,
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Another customer with this PAN already exists.")

    if update_data:
        await db.execute(
            update(Customer).where(Customer.customer_id == customer_id).values(**update_data)
        )
        await db.commit()
        await db.refresh(customer)
    return customer


async def delete_customer(db: AsyncSession, tenant_id: int, customer_id: int):
    customer = await get_customer(db, tenant_id, customer_id)
    await db.execute(
        update(Customer).where(Customer.customer_id == customer_id)
        .values(is_deleted=True, status="INACTIVE")
    )
    await db.commit()


# ─── Customer Details ─────────────────────────────────────────────────────────

async def get_or_create_details(db: AsyncSession, customer_id: int) -> CustomerDetails:
    result = await db.execute(
        select(CustomerDetails).where(CustomerDetails.customer_id == customer_id)
    )
    details = result.scalar_one_or_none()
    if not details:
        details = CustomerDetails(customer_id=customer_id)
        db.add(details)
        await db.flush()
    return details


async def update_customer_details(
    db: AsyncSession, tenant_id: int, customer_id: int, data: CustomerDetailsCreate
) -> CustomerDetails:
    await get_customer(db, tenant_id, customer_id)  # ensure ownership
    details = await get_or_create_details(db, customer_id)
    update_data = data.model_dump(exclude_unset=True)
    if update_data:
        await db.execute(
            update(CustomerDetails)
            .where(CustomerDetails.customer_id == customer_id)
            .values(**update_data)
        )
        await db.commit()
        await db.refresh(details)
    return details


# ─── KYC ─────────────────────────────────────────────────────────────────────

async def update_kyc_status(
    db: AsyncSession, tenant_id: int, customer_id: int, status: str
) -> Customer:
    customer = await get_customer(db, tenant_id, customer_id)
    values = {"kyc_status": status}
    if status == "VERIFIED":
        values["kyc_verified_at"] = datetime.now(timezone.utc)
    await db.execute(
        update(Customer).where(Customer.customer_id == customer_id).values(**values)
    )
    await db.commit()
    await db.refresh(customer)
    return customer


# ─── Stats ───────────────────────────────────────────────────────────────────

async def get_customer_stats(db: AsyncSession, tenant_id: int) -> dict:
    total_q = await db.execute(
        select(func.count(Customer.customer_id)).where(
            Customer.tenant_id == tenant_id, Customer.is_deleted == False
        )
    )
    active_q = await db.execute(
        select(func.count(Customer.customer_id)).where(
            Customer.tenant_id == tenant_id,
            Customer.is_deleted == False,
            Customer.status == "ACTIVE",
        )
    )
    kyc_pending_q = await db.execute(
        select(func.count(Customer.customer_id)).where(
            Customer.tenant_id == tenant_id,
            Customer.is_deleted == False,
            Customer.kyc_status == "PENDING",
        )
    )
    type_q = await db.execute(
        select(Customer.customer_type, func.count(Customer.customer_id))
        .where(Customer.tenant_id == tenant_id, Customer.is_deleted == False)
        .group_by(Customer.customer_type)
    )

    return {
        "total": total_q.scalar(),
        "active": active_q.scalar(),
        "kyc_pending": kyc_pending_q.scalar(),
        "by_type": {row[0]: row[1] for row in type_q.fetchall()},
    }
