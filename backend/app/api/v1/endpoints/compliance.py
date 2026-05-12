from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.deps import get_db, get_current_active_user
from app.models.auth import User
from app.schemas.compliance import (
    ComplianceCreate, ComplianceUpdate, ComplianceResponse, ComplianceDetailedResponse,
    ComplianceTaskCreate, ComplianceTaskUpdate, ComplianceTaskResponse,
    ComplianceReminderCreate, ComplianceReminderUpdate, ComplianceReminderResponse,
    ComplianceSummary, ComplianceTaskSummary
)
from app.services.compliance import ComplianceService, ComplianceTaskService, ComplianceReminderService

router = APIRouter(prefix="/compliance", tags=["compliance"])


# ─── Compliance Endpoints ────────────────────────────────────────────────────

@router.post("/", response_model=ComplianceResponse, status_code=status.HTTP_201_CREATED)
def create_compliance(
    compliance_data: ComplianceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new compliance record"""
    compliance = ComplianceService.create_compliance(
        db, current_user.tenant_id, compliance_data, current_user.user_id
    )
    return compliance


@router.get("/{compliance_id}", response_model=ComplianceDetailedResponse)
def get_compliance(
    compliance_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get compliance details with related tasks and history"""
    compliance = ComplianceService.get_compliance(db, current_user.tenant_id, compliance_id)
    if not compliance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compliance not found")
    
    return compliance


@router.get("/customer/{customer_id}", response_model=List[ComplianceResponse])
def get_customer_compliances(
    customer_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all compliances for a customer"""
    compliances = ComplianceService.get_customer_compliances(
        db, current_user.tenant_id, customer_id
    )
    return compliances


@router.get("/", response_model=List[ComplianceResponse])
def list_compliances(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all compliances for tenant"""
    compliances = ComplianceService.get_tenant_compliances(
        db, current_user.tenant_id, skip, limit
    )
    return compliances


@router.put("/{compliance_id}", response_model=ComplianceResponse)
def update_compliance(
    compliance_id: UUID,
    compliance_data: ComplianceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update compliance record"""
    compliance = ComplianceService.update_compliance(
        db, current_user.tenant_id, compliance_id, compliance_data, current_user.user_id
    )
    if not compliance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compliance not found")
    
    return compliance


@router.delete("/{compliance_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_compliance(
    compliance_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete compliance record"""
    success = ComplianceService.delete_compliance(
        db, current_user.tenant_id, compliance_id, current_user.user_id
    )
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compliance not found")


@router.get("/summary/dashboard", response_model=ComplianceSummary)
def get_compliance_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get compliance summary for dashboard"""
    summary = ComplianceService.get_compliance_summary(db, current_user.tenant_id)
    return summary


# ─── Compliance Task Endpoints ───────────────────────────────────────────────

@router.post("/task/", response_model=ComplianceTaskResponse, status_code=status.HTTP_201_CREATED)
def create_compliance_task(
    task_data: ComplianceTaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new compliance task"""
    task = ComplianceTaskService.create_compliance_task(
        db, current_user.tenant_id, task_data, current_user.user_id
    )
    return task


@router.get("/task/{compliance_task_id}", response_model=ComplianceTaskResponse)
def get_compliance_task(
    compliance_task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get compliance task details"""
    task = ComplianceTaskService.get_compliance_task(
        db, current_user.tenant_id, compliance_task_id
    )
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    return task


@router.get("/{compliance_id}/tasks", response_model=List[ComplianceTaskResponse])
def get_compliance_tasks(
    compliance_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all tasks for a compliance"""
    tasks = ComplianceTaskService.get_compliance_tasks(
        db, current_user.tenant_id, compliance_id
    )
    return tasks


@router.get("/employee/tasks", response_model=List[ComplianceTaskResponse])
def get_my_compliance_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all compliance tasks assigned to current employee"""
    tasks = ComplianceTaskService.get_employee_compliance_tasks(
        db, current_user.tenant_id, current_user.user_id
    )
    return tasks


@router.put("/task/{compliance_task_id}", response_model=ComplianceTaskResponse)
def update_compliance_task(
    compliance_task_id: UUID,
    task_data: ComplianceTaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update compliance task"""
    task = ComplianceTaskService.update_compliance_task(
        db, current_user.tenant_id, compliance_task_id, task_data
    )
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    return task


@router.post("/task/{compliance_task_id}/submit", response_model=ComplianceTaskResponse)
def submit_compliance_task(
    compliance_task_id: UUID,
    documents: dict = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Submit compliance task with documents"""
    task = ComplianceTaskService.submit_compliance_task(
        db, current_user.tenant_id, compliance_task_id, documents
    )
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    return task


@router.post("/task/{compliance_task_id}/approve", response_model=ComplianceTaskResponse)
def approve_compliance_task(
    compliance_task_id: UUID,
    comments: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Approve compliance task"""
    task = ComplianceTaskService.approve_compliance_task(
        db, current_user.tenant_id, compliance_task_id, current_user.user_id, comments
    )
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    return task


@router.post("/task/{compliance_task_id}/reject", response_model=ComplianceTaskResponse)
def reject_compliance_task(
    compliance_task_id: UUID,
    comments: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Reject compliance task"""
    task = ComplianceTaskService.reject_compliance_task(
        db, current_user.tenant_id, compliance_task_id, current_user.user_id, comments
    )
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    return task


@router.get("/task/summary/dashboard", response_model=ComplianceTaskSummary)
def get_compliance_task_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get compliance task summary for dashboard"""
    summary = ComplianceTaskService.get_compliance_task_summary(db, current_user.tenant_id)
    return summary


# ─── Compliance Reminder Endpoints ───────────────────────────────────────────

@router.post("/reminder/", response_model=ComplianceReminderResponse, status_code=status.HTTP_201_CREATED)
def create_reminder(
    reminder_data: ComplianceReminderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new compliance reminder"""
    reminder = ComplianceReminderService.create_reminder(
        db, current_user.tenant_id, reminder_data
    )
    return reminder


@router.get("/reminder/pending", response_model=List[ComplianceReminderResponse])
def get_pending_reminders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all pending reminders for today"""
    reminders = ComplianceReminderService.get_pending_reminders(
        db, current_user.tenant_id
    )
    return reminders


@router.post("/reminder/{reminder_id}/mark-sent", response_model=ComplianceReminderResponse)
def mark_reminder_sent(
    reminder_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mark reminder as sent"""
    reminder = ComplianceReminderService.mark_reminder_sent(db, reminder_id)
    if not reminder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")
    
    return reminder


@router.post("/reminder/{reminder_id}/acknowledge", response_model=ComplianceReminderResponse)
def acknowledge_reminder(
    reminder_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Acknowledge reminder"""
    reminder = ComplianceReminderService.acknowledge_reminder(db, reminder_id)
    if not reminder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")
    
    return reminder
