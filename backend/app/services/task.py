from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, or_, and_, case
from fastapi import HTTPException
from datetime import datetime, timezone, date, timedelta
from typing import Optional, List, Tuple

from app.models.task import Task, TaskDetail, TaskReminder
from app.schemas.task import TaskCreate, TaskUpdate, TaskDetailCreate, TaskDetailUpdate, ReminderCreate


# ─── Task CRUD ────────────────────────────────────────────────────────────────

async def get_tasks(
    db: AsyncSession,
    tenant_id: int,
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    task_type_code: Optional[str] = None,
    customer_id: Optional[int] = None,
    assigned_to_user_id: Optional[int] = None,
    financial_year: Optional[str] = None,
    overdue_only: bool = False,
    due_today: bool = False,
) -> Tuple[List[Task], int]:
    query = select(Task).where(
        Task.tenant_id == tenant_id,
        Task.is_deleted == False,
    )

    if search:
        query = query.where(
            or_(
                Task.task_title.ilike(f"%{search}%"),
                Task.task_type_code.ilike(f"%{search}%"),
                Task.return_period.ilike(f"%{search}%"),
                Task.financial_year.ilike(f"%{search}%"),
            )
        )
    if status:
        query = query.where(Task.status == status)
    if priority:
        query = query.where(Task.priority == priority)
    if task_type_code:
        query = query.where(Task.task_type_code == task_type_code)
    if customer_id:
        query = query.where(Task.customer_id == customer_id)
    if assigned_to_user_id:
        query = query.where(Task.assigned_to_user_id == assigned_to_user_id)
    if financial_year:
        query = query.where(Task.financial_year == financial_year)
    if overdue_only:
        query = query.where(
            Task.due_date < date.today(),
            Task.status.not_in(["COMPLETED", "FILED", "CANCELLED"]),
        )
    if due_today:
        query = query.where(Task.due_date == date.today())

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()

    query = (
        query
        .offset((page - 1) * page_size)
        .limit(page_size)
        .order_by(Task.due_date.asc(), Task.priority.desc())
    )
    result = await db.execute(query)
    return result.scalars().all(), total


async def get_client_tasks(
    db: AsyncSession,
    tenant_id: int,
    user_email: str,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Task], int]:
    """Get tasks assigned to a client/customer by their email"""
    from app.models.customer import Customer
    
    # Find customer by email
    customer_result = await db.execute(
        select(Customer).where(
            Customer.tenant_id == tenant_id,
            Customer.email == user_email,
            Customer.is_deleted == False,
        )
    )
    customer = customer_result.scalar_one_or_none()
    
    if not customer:
        return [], 0
    
    # Get tasks for this customer
    query = select(Task).where(
        Task.tenant_id == tenant_id,
        Task.customer_id == customer.customer_id,
        Task.is_deleted == False,
    )
    
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()
    
    query = (
        query
        .offset((page - 1) * page_size)
        .limit(page_size)
        .order_by(Task.due_date.asc(), Task.priority.desc())
    )
    result = await db.execute(query)
    return result.scalars().all(), total


async def get_employee_tasks(
    db: AsyncSession,
    tenant_id: int,
    user_id: int,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Task], int]:
    """Get tasks assigned to an employee by their user_id"""
    # Get tasks assigned to this employee
    query = select(Task).where(
        Task.tenant_id == tenant_id,
        Task.assigned_to_user_id == user_id,
        Task.is_deleted == False,
    )
    
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()
    
    query = (
        query
        .offset((page - 1) * page_size)
        .limit(page_size)
        .order_by(Task.due_date.asc(), Task.priority.desc())
    )
    result = await db.execute(query)
    return result.scalars().all(), total


async def get_task(db: AsyncSession, tenant_id: int, task_id: int) -> Task:
    result = await db.execute(
        select(Task).where(
            Task.task_id == task_id,
            Task.tenant_id == tenant_id,
            Task.is_deleted == False,
        )
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    return task


async def create_task(db: AsyncSession, tenant_id: int, data: TaskCreate) -> Task:
    task_data = data.model_dump(exclude={"steps"})
    task = Task(tenant_id=tenant_id, **task_data)
    db.add(task)
    await db.flush()

    # Create default checklist steps from template or provided steps
    steps = data.steps or _get_default_steps(data.task_type_code)
    for i, step in enumerate(steps):
        step_data = step if isinstance(step, dict) else step.model_dump()
        step_data["step_order"] = i
        detail = TaskDetail(
            task_id=task.task_id,
            tenant_id=tenant_id,
            **step_data,
        )
        db.add(detail)

    await db.commit()
    await db.refresh(task)
    return task


async def update_task(
    db: AsyncSession, tenant_id: int, task_id: int, data: TaskUpdate
) -> Task:
    task = await get_task(db, tenant_id, task_id)
    update_data = data.model_dump(exclude_unset=True)

    # Auto-set filed_at when status → FILED
    if update_data.get("status") == "FILED" and not task.filed_at:
        update_data["filed_at"] = datetime.now(timezone.utc)

    # Auto-complete percentage
    if update_data.get("status") in ("COMPLETED", "FILED"):
        update_data.setdefault("completion_percentage", 100)
    elif update_data.get("status") == "CANCELLED":
        pass  # keep existing percentage

    if update_data:
        await db.execute(update(Task).where(Task.task_id == task_id).values(**update_data))
        await db.commit()
        await db.refresh(task)
    return task


async def delete_task(db: AsyncSession, tenant_id: int, task_id: int):
    await get_task(db, tenant_id, task_id)
    await db.execute(
        update(Task).where(Task.task_id == task_id)
        .values(is_deleted=True, status="CANCELLED")
    )
    await db.commit()


# ─── Task Details (Steps) ─────────────────────────────────────────────────────

async def add_task_step(
    db: AsyncSession, tenant_id: int, task_id: int, data: TaskDetailCreate
) -> TaskDetail:
    await get_task(db, tenant_id, task_id)
    detail = TaskDetail(task_id=task_id, tenant_id=tenant_id, **data.model_dump())
    db.add(detail)
    await db.commit()
    await db.refresh(detail)
    return detail


async def update_task_step(
    db: AsyncSession, tenant_id: int, task_id: int, step_id: int, data: TaskDetailUpdate
) -> TaskDetail:
    result = await db.execute(
        select(TaskDetail).where(
            TaskDetail.task_detail_id == step_id,
            TaskDetail.task_id == task_id,
            TaskDetail.tenant_id == tenant_id,
        )
    )
    step = result.scalar_one_or_none()
    if not step:
        raise HTTPException(status_code=404, detail="Task step not found.")

    update_data = data.model_dump(exclude_unset=True)
    now = datetime.now(timezone.utc)

    if update_data.get("status") == "COMPLETED" and not step.completed_at:
        update_data["completed_at"] = now

    if update_data:
        await db.execute(
            update(TaskDetail).where(TaskDetail.task_detail_id == step_id).values(**update_data)
        )
        await db.commit()
        await db.refresh(step)

    # Recalculate parent task completion %
    await _recalculate_task_completion(db, task_id)
    return step


async def delete_task_step(db: AsyncSession, tenant_id: int, task_id: int, step_id: int):
    result = await db.execute(
        select(TaskDetail).where(
            TaskDetail.task_detail_id == step_id,
            TaskDetail.task_id == task_id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Step not found.")
    await db.execute(
        update(TaskDetail).where(TaskDetail.task_detail_id == step_id)
        .values(status="SKIPPED")
    )
    await db.commit()


async def _recalculate_task_completion(db: AsyncSession, task_id: int):
    result = await db.execute(
        select(
            func.count(TaskDetail.task_detail_id).label("total"),
            func.sum(case((TaskDetail.status == "COMPLETED", 1), else_=0)).label("done"),
        ).where(
            TaskDetail.task_id == task_id,
            TaskDetail.is_required == True,
            TaskDetail.status != "SKIPPED",
        )
    )
    row = result.one_or_none()
    if row and row.total:
        pct = int((row.done / row.total) * 100)
        new_status = None
        if pct == 100:
            new_status = "COMPLETED"
        elif pct > 0:
            new_status = "IN_PROGRESS"
        vals = {"completion_percentage": pct}
        if new_status:
            vals["status"] = new_status
        await db.execute(update(Task).where(Task.task_id == task_id).values(**vals))
        await db.commit()


# ─── Reminders ────────────────────────────────────────────────────────────────

async def create_reminder(
    db: AsyncSession, tenant_id: int, task_id: int,
    data: ReminderCreate, created_by: int
) -> TaskReminder:
    await get_task(db, tenant_id, task_id)
    reminder = TaskReminder(
        tenant_id=tenant_id,
        task_id=task_id,
        created_by_user_id=created_by,
        **data.model_dump(),
    )
    db.add(reminder)
    await db.commit()
    await db.refresh(reminder)
    return reminder


async def get_task_reminders(db: AsyncSession, task_id: int) -> List[TaskReminder]:
    result = await db.execute(
        select(TaskReminder).where(TaskReminder.task_id == task_id)
        .order_by(TaskReminder.scheduled_at)
    )
    return result.scalars().all()


# ─── Stats ────────────────────────────────────────────────────────────────────

async def get_task_stats(db: AsyncSession, tenant_id: int) -> dict:
    today = date.today()
    week_end = today + timedelta(days=7)

    base = and_(Task.tenant_id == tenant_id, Task.is_deleted == False)

    total_q   = await db.execute(select(func.count(Task.task_id)).where(base))
    pending_q = await db.execute(select(func.count(Task.task_id)).where(base, Task.status == "PENDING"))
    inprog_q  = await db.execute(select(func.count(Task.task_id)).where(base, Task.status == "IN_PROGRESS"))
    done_q    = await db.execute(select(func.count(Task.task_id)).where(base, Task.status.in_(["COMPLETED", "FILED"])))
    overdue_q = await db.execute(select(func.count(Task.task_id)).where(
        base, Task.due_date < today, Task.status.not_in(["COMPLETED", "FILED", "CANCELLED"])
    ))
    today_q   = await db.execute(select(func.count(Task.task_id)).where(
        base, Task.due_date == today, Task.status.not_in(["COMPLETED", "FILED", "CANCELLED"])
    ))
    week_q    = await db.execute(select(func.count(Task.task_id)).where(
        base, Task.due_date.between(today, week_end), Task.status.not_in(["COMPLETED", "FILED", "CANCELLED"])
    ))
    by_status_q = await db.execute(
        select(Task.status, func.count(Task.task_id)).where(base).group_by(Task.status)
    )
    by_priority_q = await db.execute(
        select(Task.priority, func.count(Task.task_id)).where(base).group_by(Task.priority)
    )
    by_type_q = await db.execute(
        select(Task.task_type_code, func.count(Task.task_id))
        .where(base).group_by(Task.task_type_code).order_by(func.count(Task.task_id).desc()).limit(10)
    )

    return {
        "total":         total_q.scalar(),
        "pending":       pending_q.scalar(),
        "in_progress":   inprog_q.scalar(),
        "completed":     done_q.scalar(),
        "overdue":       overdue_q.scalar(),
        "due_today":     today_q.scalar(),
        "due_this_week": week_q.scalar(),
        "by_status":     {r[0]: r[1] for r in by_status_q.fetchall()},
        "by_priority":   {r[0]: r[1] for r in by_priority_q.fetchall()},
        "by_type":       {r[0]: r[1] for r in by_type_q.fetchall()},
    }


# ─── Default checklist templates ─────────────────────────────────────────────

def _get_default_steps(task_type: str) -> List[dict]:
    templates = {
        "GSTR1": [
            {"step_title": "Collect sales invoices from client", "is_client_action": True},
            {"step_title": "Prepare B2B / B2C data in template"},
            {"step_title": "Reconcile with purchase register"},
            {"step_title": "Upload JSON to GST portal"},
            {"step_title": "Submit and download acknowledgement"},
        ],
        "GSTR3B": [
            {"step_title": "Collect purchase bills and ITC data", "is_client_action": True},
            {"step_title": "Calculate output tax liability"},
            {"step_title": "Verify ITC eligibility"},
            {"step_title": "File GSTR-3B and pay tax"},
            {"step_title": "Download filed return copy"},
        ],
        "ITR1": [
            {"step_title": "Collect Form 16 from client", "is_client_action": True},
            {"step_title": "Collect bank statements and interest certificates", "is_client_action": True},
            {"step_title": "Prepare income computation"},
            {"step_title": "Verify 26AS / AIS / TIS"},
            {"step_title": "File ITR on income tax portal"},
            {"step_title": "Download ITR-V acknowledgement"},
            {"step_title": "E-verify return"},
        ],
        "TDS_RETURN_26Q": [
            {"step_title": "Collect TDS deduction details", "is_client_action": True},
            {"step_title": "Verify PAN of deductees"},
            {"step_title": "Prepare FVU file using TRACES"},
            {"step_title": "Validate and upload to TRACES"},
            {"step_title": "Download 27A acknowledgement"},
        ],
        "AUDIT_TAX": [
            {"step_title": "Collect books of accounts and financials", "is_client_action": True},
            {"step_title": "Review P&L and Balance Sheet"},
            {"step_title": "Prepare Tax Audit report (Form 3CD)"},
            {"step_title": "Get client sign-off on report", "is_client_action": True},
            {"step_title": "Upload Form 3CB/3CD on income tax portal"},
        ],
    }
    default = [
        {"step_title": "Collect required documents from client", "is_client_action": True},
        {"step_title": "Process and prepare filing"},
        {"step_title": "Review and verify"},
        {"step_title": "Submit filing"},
        {"step_title": "Download acknowledgement"},
    ]
    return [{"step_order": i, **s} for i, s in enumerate(templates.get(task_type, default))]
