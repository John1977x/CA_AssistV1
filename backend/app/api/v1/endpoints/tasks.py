from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import math

from app.db.session import get_db
from app.core.deps import get_current_active_user
from app.models.auth import User
from app.schemas.task import (
    TaskCreate, TaskUpdate, TaskOut, TaskListOut,
    TaskDetailCreate, TaskDetailUpdate, TaskDetailOut,
    ReminderCreate, ReminderOut,
    PaginatedResponse, MessageResponse,
)
from app.services import task as svc

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("/stats")
async def task_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return await svc.get_task_stats(db, current_user.tenant_id)


@router.get("/client/assigned", response_model=PaginatedResponse)
async def get_client_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get tasks assigned to the current client/customer"""
    tasks, total = await svc.get_client_tasks(
        db, current_user.tenant_id, current_user.email, page, page_size
    )
    return PaginatedResponse(
        items=[TaskListOut.model_validate(t) for t in tasks],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total else 1,
    )


@router.get("/employee/assigned", response_model=PaginatedResponse)
async def get_employee_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get tasks assigned to the current employee"""
    tasks, total = await svc.get_employee_tasks(
        db, current_user.tenant_id, current_user.user_id, page, page_size
    )
    return PaginatedResponse(
        items=[TaskListOut.model_validate(t) for t in tasks],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total else 1,
    )


@router.get("", response_model=PaginatedResponse)
async def list_tasks(
    page:                int           = Query(1, ge=1),
    page_size:           int           = Query(20, ge=1, le=100),
    search:              Optional[str] = Query(None),
    status:              Optional[str] = Query(None),
    priority:            Optional[str] = Query(None),
    task_type_code:      Optional[str] = Query(None),
    customer_id:         Optional[int] = Query(None),
    assigned_to_user_id: Optional[int] = Query(None),
    financial_year:      Optional[str] = Query(None),
    overdue_only:        bool          = Query(False),
    due_today:           bool          = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    tasks, total = await svc.get_tasks(
        db, current_user.tenant_id, page, page_size,
        search, status, priority, task_type_code,
        customer_id, assigned_to_user_id, financial_year,
        overdue_only, due_today,
    )
    return PaginatedResponse(
        items=[TaskListOut.model_validate(t) for t in tasks],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total else 1,
    )


@router.post("", response_model=TaskOut, status_code=201)
async def create_task(
    data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    task = await svc.create_task(db, current_user.tenant_id, data)
    return TaskOut.model_validate(task)


@router.get("/{task_id}", response_model=TaskOut)
async def get_task(
    task_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    task = await svc.get_task(db, current_user.tenant_id, task_id)
    return TaskOut.model_validate(task)


@router.patch("/{task_id}", response_model=TaskOut)
async def update_task(
    data: TaskUpdate,
    task_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    task = await svc.update_task(db, current_user.tenant_id, task_id, data)
    return TaskOut.model_validate(task)


@router.delete("/{task_id}", response_model=MessageResponse)
async def delete_task(
    task_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    await svc.delete_task(db, current_user.tenant_id, task_id)
    return MessageResponse(message="Task cancelled.")


# ─── Steps ────────────────────────────────────────────────────────────────────

@router.post("/{task_id}/steps", response_model=TaskDetailOut, status_code=201)
async def add_step(
    data: TaskDetailCreate,
    task_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    step = await svc.add_task_step(db, current_user.tenant_id, task_id, data)
    return TaskDetailOut.model_validate(step)


@router.patch("/{task_id}/steps/{step_id}", response_model=TaskDetailOut)
async def update_step(
    data: TaskDetailUpdate,
    task_id: int = Path(...),
    step_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    step = await svc.update_task_step(db, current_user.tenant_id, task_id, step_id, data)
    return TaskDetailOut.model_validate(step)


@router.delete("/{task_id}/steps/{step_id}", response_model=MessageResponse)
async def delete_step(
    task_id: int = Path(...),
    step_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    await svc.delete_task_step(db, current_user.tenant_id, task_id, step_id)
    return MessageResponse(message="Step skipped.")


# ─── Reminders ────────────────────────────────────────────────────────────────

@router.get("/{task_id}/reminders", response_model=list)
async def list_reminders(
    task_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    reminders = await svc.get_task_reminders(db, task_id)
    return [ReminderOut.model_validate(r) for r in reminders]


@router.post("/{task_id}/reminders", response_model=ReminderOut, status_code=201)
async def create_reminder(
    data: ReminderCreate,
    task_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    reminder = await svc.create_reminder(
        db, current_user.tenant_id, task_id, data, current_user.user_id
    )
    return ReminderOut.model_validate(reminder)
