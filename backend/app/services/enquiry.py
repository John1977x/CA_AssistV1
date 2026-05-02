from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, or_
from fastapi import HTTPException
from datetime import datetime, timezone, date as date_type
from typing import Optional, List, Tuple

from app.models.customer import Enquiry, Customer, CustomerDetails
from app.schemas.customer import EnquiryCreate, EnquiryUpdate, EnquiryConvertRequest
from app.services.customer import _generate_customer_code


async def _generate_enquiry_number(db: AsyncSession, tenant_id: int) -> str:
    result = await db.execute(
        select(func.count(Enquiry.enquiry_id)).where(Enquiry.tenant_id == tenant_id)
    )
    count = result.scalar() or 0
    return f"ENQ-{str(count + 1).zfill(4)}"


async def get_enquiries(
    db: AsyncSession,
    tenant_id: int,
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None,
    status: Optional[str] = None,
    source: Optional[str] = None,
    assigned_to_user_id: Optional[int] = None,
    is_converted: Optional[bool] = None,
) -> Tuple[List[Enquiry], int]:
    query = select(Enquiry).where(Enquiry.tenant_id == tenant_id)

    if search:
        query = query.where(
            or_(
                Enquiry.full_name.ilike(f"%{search}%"),
                Enquiry.email.ilike(f"%{search}%"),
                Enquiry.phone.ilike(f"%{search}%"),
                Enquiry.company_name.ilike(f"%{search}%"),
                Enquiry.enquiry_number.ilike(f"%{search}%"),
            )
        )
    if status:
        query = query.where(Enquiry.status == status)
    if source:
        query = query.where(Enquiry.source == source)
    if assigned_to_user_id:
        query = query.where(Enquiry.assigned_to_user_id == assigned_to_user_id)
    if is_converted is not None:
        query = query.where(Enquiry.is_converted == is_converted)

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()

    query = query.offset((page - 1) * page_size).limit(page_size).order_by(Enquiry.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all(), total


async def get_enquiry(db: AsyncSession, tenant_id: int, enquiry_id: int) -> Enquiry:
    result = await db.execute(
        select(Enquiry).where(
            Enquiry.enquiry_id == enquiry_id,
            Enquiry.tenant_id == tenant_id,
        )
    )
    enq = result.scalar_one_or_none()
    if not enq:
        raise HTTPException(status_code=404, detail="Enquiry not found.")
    return enq


async def create_enquiry(db: AsyncSession, tenant_id: int, data: EnquiryCreate) -> Enquiry:
    number = await _generate_enquiry_number(db, tenant_id)
    enq_data = data.model_dump()
    enq_data["enquiry_date"] = enq_data.get("enquiry_date") or date_type.today()

    enquiry = Enquiry(
        tenant_id=tenant_id,
        enquiry_number=number,
        **enq_data,
    )
    db.add(enquiry)
    await db.commit()
    await db.refresh(enquiry)
    return enquiry


async def update_enquiry(
    db: AsyncSession, tenant_id: int, enquiry_id: int, data: EnquiryUpdate
) -> Enquiry:
    enquiry = await get_enquiry(db, tenant_id, enquiry_id)
    if enquiry.is_converted:
        raise HTTPException(status_code=400, detail="Cannot edit a converted enquiry.")

    update_data = data.model_dump(exclude_unset=True)
    if update_data:
        await db.execute(
            update(Enquiry).where(Enquiry.enquiry_id == enquiry_id).values(**update_data)
        )
        await db.commit()
        await db.refresh(enquiry)
    return enquiry


async def delete_enquiry(db: AsyncSession, tenant_id: int, enquiry_id: int):
    enquiry = await get_enquiry(db, tenant_id, enquiry_id)
    if enquiry.is_converted:
        raise HTTPException(status_code=400, detail="Cannot delete a converted enquiry.")
    await db.execute(update(Enquiry).where(Enquiry.enquiry_id == enquiry_id).values(status="LOST"))
    await db.commit()


async def convert_enquiry(
    db: AsyncSession,
    tenant_id: int,
    enquiry_id: int,
    data: EnquiryConvertRequest,
    converted_by_user_id: int,
) -> Customer:
    enquiry = await get_enquiry(db, tenant_id, enquiry_id)
    if enquiry.is_converted:
        raise HTTPException(status_code=400, detail="Enquiry is already converted.")

    code = await _generate_customer_code(db, tenant_id)
    now = datetime.now(timezone.utc)

    customer = Customer(
        tenant_id=tenant_id,
        customer_code=code,
        customer_type=data.customer_type,
        display_name=data.display_name or enquiry.full_name,
        legal_name=data.display_name or enquiry.full_name,
        pan=data.pan,
        gstin=data.gstin,
        email=enquiry.email,
        phone=enquiry.phone,
        source_channel=enquiry.source,
        notes=enquiry.message,
        onboarded_at=data.onboarded_at or date_type.today(),
        assigned_user_id=data.assigned_user_id or enquiry.assigned_to_user_id,
        branch_id=data.branch_id or enquiry.branch_id,
        status="ACTIVE",
    )
    db.add(customer)
    await db.flush()

    # Create empty details
    details = CustomerDetails(customer_id=customer.customer_id)
    db.add(details)

    # Mark enquiry as converted
    await db.execute(
        update(Enquiry).where(Enquiry.enquiry_id == enquiry_id).values(
            is_converted=True,
            converted_customer_id=customer.customer_id,
            converted_at=now,
            converted_by_user_id=converted_by_user_id,
            status="WON",
        )
    )
    await db.commit()
    await db.refresh(customer)
    return customer


async def get_enquiry_stats(db: AsyncSession, tenant_id: int) -> dict:
    total_q = await db.execute(
        select(func.count(Enquiry.enquiry_id)).where(Enquiry.tenant_id == tenant_id)
    )
    new_q = await db.execute(
        select(func.count(Enquiry.enquiry_id)).where(
            Enquiry.tenant_id == tenant_id, Enquiry.status == "NEW"
        )
    )
    converted_q = await db.execute(
        select(func.count(Enquiry.enquiry_id)).where(
            Enquiry.tenant_id == tenant_id, Enquiry.is_converted == True
        )
    )
    by_status_q = await db.execute(
        select(Enquiry.status, func.count(Enquiry.enquiry_id))
        .where(Enquiry.tenant_id == tenant_id)
        .group_by(Enquiry.status)
    )
    return {
        "total": total_q.scalar(),
        "new": new_q.scalar(),
        "converted": converted_q.scalar(),
        "by_status": {r[0]: r[1] for r in by_status_q.fetchall()},
    }
