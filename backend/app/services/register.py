from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, or_
from fastapi import HTTPException
from datetime import datetime, timezone
from typing import Optional, List, Tuple

from app.models.register import Register
from app.schemas.register import RegisterCreate, RegisterUpdate


async def create_register(
    db: AsyncSession, tenant_id: int, data: RegisterCreate
) -> Register:
    entry = Register(tenant_id=tenant_id, **data.model_dump())
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


async def get_registers(
    db: AsyncSession,
    tenant_id: int,
    page: int = 1,
    page_size: int = 20,
    in_out_ward: Optional[str] = None,
    doc_type: Optional[str] = None,
    search: Optional[str] = None,
    filter_employee_id: Optional[int] = None,
    filter_client_id: Optional[int] = None,
) -> Tuple[List[Register], int]:
    query = select(Register).where(
        Register.tenant_id == tenant_id,
        Register.is_deleted == False,
    )
    if filter_employee_id is not None:
        query = query.where(Register.employee_id == filter_employee_id)
    if filter_client_id is not None:
        query = query.where(Register.client_id == filter_client_id)
    if in_out_ward:
        query = query.where(Register.in_out_ward == in_out_ward)
    if doc_type:
        query = query.where(Register.doc_type == doc_type)
    if search:
        query = query.where(
            or_(
                Register.doc_description.ilike(f"%{search}%"),
                Register.acknowledgement.ilike(f"%{search}%"),
            )
        )

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()

    query = query.order_by(Register.doc_date.desc(), Register.register_id.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    return result.scalars().all(), total


async def get_register(db: AsyncSession, tenant_id: int, register_id: int) -> Register:
    result = await db.execute(
        select(Register).where(
            Register.register_id == register_id,
            Register.tenant_id == tenant_id,
            Register.is_deleted == False,
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Register entry not found.")
    return entry


async def update_register(
    db: AsyncSession, tenant_id: int, register_id: int, data: RegisterUpdate
) -> Register:
    entry = await get_register(db, tenant_id, register_id)
    update_data = data.model_dump(exclude_unset=True)
    if update_data:
        await db.execute(
            update(Register)
            .where(Register.register_id == register_id)
            .values(**update_data)
        )
        await db.commit()
        await db.refresh(entry)
    return entry


async def delete_register(db: AsyncSession, tenant_id: int, register_id: int):
    await get_register(db, tenant_id, register_id)
    await db.execute(
        update(Register)
        .where(Register.register_id == register_id)
        .values(is_deleted=True)
    )
    await db.commit()


async def get_stats(
    db: AsyncSession,
    tenant_id: int,
    filter_employee_id: Optional[int] = None,
    filter_client_id: Optional[int] = None,
) -> dict:
    base = [Register.tenant_id == tenant_id, Register.is_deleted == False]
    if filter_employee_id is not None:
        base.append(Register.employee_id == filter_employee_id)
    if filter_client_id is not None:
        base.append(Register.client_id == filter_client_id)
    total    = (await db.execute(select(func.count(Register.register_id)).where(*base))).scalar() or 0
    inward   = (await db.execute(select(func.count(Register.register_id)).where(*base, Register.in_out_ward == "INWARD"))).scalar() or 0
    outward  = (await db.execute(select(func.count(Register.register_id)).where(*base, Register.in_out_ward == "OUTWARD"))).scalar() or 0
    pend_ack = (await db.execute(select(func.count(Register.register_id)).where(*base, Register.acknowledgement == None))).scalar() or 0
    return {"total": total, "inward": inward, "outward": outward, "pending_ack": pend_ack}
