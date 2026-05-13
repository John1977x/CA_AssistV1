from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from sqlalchemy.orm import aliased
from fastapi import HTTPException
from typing import List, Tuple, Optional

from app.models.leave import LeaveMaster, LeaveApplication
from app.models.auth import User
from app.schemas.leave import (
    LeaveMasterCreate, LeaveMasterUpdate,
    LeaveApplicationCreate, LeaveApplicationUpdate, LeaveApplicationOut,
)


# ─── Leave Master ─────────────────────────────────────────────────────────────

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


# ─── Leave Application helpers ────────────────────────────────────────────────

def _build_app_out(row) -> LeaveApplicationOut:
    app_obj, emp_name, appr_name = row
    d = {c.key: getattr(app_obj, c.key) for c in LeaveApplication.__table__.columns}
    d["employee_name"] = emp_name
    d["approver_name"] = appr_name
    return LeaveApplicationOut(**d)


def _app_joined_select():
    Employee = aliased(User)
    Approver = aliased(User)
    return (
        select(
            LeaveApplication,
            func.concat(Employee.first_name, " ", Employee.last_name).label("emp_name"),
            func.concat(Approver.first_name, " ", Approver.last_name).label("appr_name"),
        )
        .outerjoin(Employee, LeaveApplication.employee_id == Employee.user_id)
        .outerjoin(Approver, LeaveApplication.approver_id == Approver.user_id)
    )


# ─── Leave Application CRUD ───────────────────────────────────────────────────

async def create_leave_application(
    db: AsyncSession, tenant_id: int, employee_id: int, data: LeaveApplicationCreate,
) -> LeaveApplicationOut:
    entry = LeaveApplication(tenant_id=tenant_id, employee_id=employee_id, **data.model_dump())
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return await get_leave_application(db, tenant_id, entry.leave_application_id)


async def get_leave_applications(
    db: AsyncSession, tenant_id: int,
    page: int = 1, page_size: int = 20,
    employee_id: Optional[int] = None,
    status: Optional[str] = None,
) -> Tuple[List[LeaveApplicationOut], int]:
    base = _app_joined_select().where(
        LeaveApplication.tenant_id == tenant_id,
        LeaveApplication.is_deleted.isnot(True),
    )
    if employee_id:
        base = base.where(LeaveApplication.employee_id == employee_id)
    if status:
        base = base.where(LeaveApplication.status == status)

    count_q = select(func.count()).select_from(
        select(LeaveApplication)
        .where(
            LeaveApplication.tenant_id == tenant_id,
            LeaveApplication.is_deleted.isnot(True),
            *([LeaveApplication.employee_id == employee_id] if employee_id else []),
            *([LeaveApplication.status == status] if status else []),
        )
        .subquery()
    )
    total = (await db.execute(count_q)).scalar()

    base = base.order_by(LeaveApplication.created_at.desc())
    base = base.offset((page - 1) * page_size).limit(page_size)
    rows = (await db.execute(base)).all()
    return [_build_app_out(r) for r in rows], total


async def get_leave_application(
    db: AsyncSession, tenant_id: int, leave_application_id: int,
) -> LeaveApplicationOut:
    stmt = _app_joined_select().where(
        LeaveApplication.leave_application_id == leave_application_id,
        LeaveApplication.tenant_id == tenant_id,
        LeaveApplication.is_deleted.isnot(True),
    )
    row = (await db.execute(stmt)).first()
    if not row:
        raise HTTPException(status_code=404, detail="Leave application not found.")
    return _build_app_out(row)


async def update_leave_application(
    db: AsyncSession, tenant_id: int, leave_application_id: int, data: LeaveApplicationUpdate,
) -> LeaveApplicationOut:
    await get_leave_application(db, tenant_id, leave_application_id)
    update_data = data.model_dump(exclude_unset=True)
    if update_data:
        await db.execute(
            update(LeaveApplication)
            .where(LeaveApplication.leave_application_id == leave_application_id)
            .values(**update_data)
        )
        await db.commit()
    return await get_leave_application(db, tenant_id, leave_application_id)


async def delete_leave_application(
    db: AsyncSession, tenant_id: int, leave_application_id: int,
) -> None:
    await get_leave_application(db, tenant_id, leave_application_id)
    await db.execute(
        update(LeaveApplication)
        .where(LeaveApplication.leave_application_id == leave_application_id)
        .values(is_deleted=True)
    )
    await db.commit()


async def get_approvers(db: AsyncSession, tenant_id: int) -> list:
    from app.models.auth import UserRole
    result = await db.execute(
        select(User.user_id, User.first_name, User.last_name, User.display_name)
        .join(UserRole, User.role_id == UserRole.role_id)
        .where(
            User.tenant_id == tenant_id,
            User.is_deleted == False,
            User.status == "ACTIVE",
            UserRole.role_code != "CLIENT",
        )
        .order_by(User.first_name, User.last_name)
    )
    return [
        {"user_id": r.user_id, "name": r.display_name or f"{r.first_name} {r.last_name}"}
        for r in result.all()
    ]
