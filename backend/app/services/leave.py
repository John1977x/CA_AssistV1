from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from fastapi import HTTPException
from typing import List, Tuple, Optional

from app.models.leave import LeaveMaster
from app.schemas.leave import LeaveMasterCreate, LeaveMasterUpdate


async def create_leave_master(
    db: AsyncSession, tenant_id: int, data: LeaveMasterCreate
) -> LeaveMaster:
    entry = LeaveMaster(tenant_id=tenant_id, **data.model_dump())
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


async def get_leave_masters(
    db: AsyncSession, tenant_id: int,
    page: int = 1, page_size: int = 20,
    calendar_year: Optional[int] = None,
) -> Tuple[List[LeaveMaster], int]:
    query = select(LeaveMaster).where(
        LeaveMaster.tenant_id == tenant_id,
        LeaveMaster.is_deleted == False,
    )
    if calendar_year:
        query = query.where(LeaveMaster.calendar_year == calendar_year)

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar()
    query = query.order_by(LeaveMaster.calendar_year.desc(), LeaveMaster.leave_type)
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    return result.scalars().all(), total


async def get_leave_master(
    db: AsyncSession, tenant_id: int, leave_master_id: int
) -> LeaveMaster:
    result = await db.execute(
        select(LeaveMaster).where(
            LeaveMaster.leave_master_id == leave_master_id,
            LeaveMaster.tenant_id == tenant_id,
            LeaveMaster.is_deleted == False,
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Leave master entry not found.")
    return entry


async def update_leave_master(
    db: AsyncSession, tenant_id: int, leave_master_id: int, data: LeaveMasterUpdate
) -> LeaveMaster:
    entry = await get_leave_master(db, tenant_id, leave_master_id)
    update_data = data.model_dump(exclude_unset=True)
    if update_data:
        await db.execute(
            update(LeaveMaster)
            .where(LeaveMaster.leave_master_id == leave_master_id)
            .values(**update_data)
        )
        await db.commit()
        await db.refresh(entry)
    return entry


async def delete_leave_master(
    db: AsyncSession, tenant_id: int, leave_master_id: int
) -> None:
    await get_leave_master(db, tenant_id, leave_master_id)
    await db.execute(
        update(LeaveMaster)
        .where(LeaveMaster.leave_master_id == leave_master_id)
        .values(is_deleted=True)
    )
    await db.commit()
