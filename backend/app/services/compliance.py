from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import List, Optional
from datetime import date, datetime, timedelta

from app.models.compliance import Compliance, ComplianceTask, ComplianceHistory, ComplianceReminder
from app.schemas.compliance import (
    ComplianceCreate, ComplianceUpdate, ComplianceTaskCreate, ComplianceTaskUpdate,
    ComplianceReminderCreate, ComplianceReminderUpdate
)


# ─── Compliance Service ──────────────────────────────────────────────────────

class ComplianceService:
    """Service for compliance operations"""

    @staticmethod
    def create_compliance(db: Session, tenant_id: int, compliance_data: ComplianceCreate, user_id: int) -> Compliance:
        """Create a new compliance record"""
        compliance = Compliance(
            tenant_id=tenant_id,
            customer_id=compliance_data.customer_id,
            compliance_type=compliance_data.compliance_type,
            compliance_code=compliance_data.compliance_code,
            pan=compliance_data.pan,
            tan=compliance_data.tan,
            gstin=compliance_data.gstin,
            gst_registration_type=compliance_data.gst_registration_type,
            gst_registration_date=compliance_data.gst_registration_date,
            gst_cancellation_date=compliance_data.gst_cancellation_date,
            tds_deductor_type=compliance_data.tds_deductor_type,
            tds_circle_code=compliance_data.tds_circle_code,
            cin=compliance_data.cin,
            company_registration_date=compliance_data.company_registration_date,
            financial_year=compliance_data.financial_year,
            financial_year_start=compliance_data.financial_year_start,
            financial_year_end=compliance_data.financial_year_end,
            status=compliance_data.status,
            compliance_status=compliance_data.compliance_status,
            last_filing_date=compliance_data.last_filing_date,
            next_filing_date=compliance_data.next_filing_date,
            filing_frequency=compliance_data.filing_frequency,
            registration_number=compliance_data.registration_number,
            registration_certificate_url=compliance_data.registration_certificate_url,
            documents_json=compliance_data.documents_json,
            contact_person_name=compliance_data.contact_person_name,
            contact_person_email=compliance_data.contact_person_email,
            contact_person_phone=compliance_data.contact_person_phone,
            registered_address=compliance_data.registered_address,
            notes=compliance_data.notes,
            custom_fields_json=compliance_data.custom_fields_json,
            created_by_user_id=user_id,
            updated_by_user_id=user_id
        )
        db.add(compliance)
        db.commit()
        db.refresh(compliance)
        
        # Log creation in history
        ComplianceService.log_history(
            db, tenant_id, compliance.compliance_id, "CREATED", 
            None, None, user_id, "Compliance record created"
        )
        
        return compliance

    @staticmethod
    def get_compliance(db: Session, tenant_id: int, compliance_id: int) -> Optional[Compliance]:
        """Get compliance by ID"""
        return db.query(Compliance).filter(
            and_(
                Compliance.compliance_id == compliance_id,
                Compliance.tenant_id == tenant_id,
                Compliance.is_deleted == False
            )
        ).first()

    @staticmethod
    def get_customer_compliances(db: Session, tenant_id: int, customer_id: int) -> List[Compliance]:
        """Get all compliances for a customer"""
        return db.query(Compliance).filter(
            and_(
                Compliance.tenant_id == tenant_id,
                Compliance.customer_id == customer_id,
                Compliance.is_deleted == False
            )
        ).order_by(desc(Compliance.created_at)).all()

    @staticmethod
    def get_tenant_compliances(db: Session, tenant_id: int, skip: int = 0, limit: int = 100) -> List[Compliance]:
        """Get all compliances for a tenant"""
        return db.query(Compliance).filter(
            and_(
                Compliance.tenant_id == tenant_id,
                Compliance.is_deleted == False
            )
        ).order_by(desc(Compliance.created_at)).offset(skip).limit(limit).all()

    @staticmethod
    def update_compliance(db: Session, tenant_id: int, compliance_id: int, 
                         compliance_data: ComplianceUpdate, user_id: int) -> Optional[Compliance]:
        """Update compliance record"""
        compliance = ComplianceService.get_compliance(db, tenant_id, compliance_id)
        if not compliance:
            return None

        # Track changes for history
        update_data = compliance_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                old_value = getattr(compliance, field)
                setattr(compliance, field, value)
                
                # Log change in history
                if old_value != value:
                    ComplianceService.log_history(
                        db, tenant_id, compliance_id, "UPDATED",
                        field, str(old_value), user_id, f"Field {field} updated"
                    )

        compliance.updated_by_user_id = user_id
        db.commit()
        db.refresh(compliance)
        return compliance

    @staticmethod
    def delete_compliance(db: Session, tenant_id: int, compliance_id: int, user_id: int) -> bool:
        """Soft delete compliance record"""
        compliance = ComplianceService.get_compliance(db, tenant_id, compliance_id)
        if not compliance:
            return False

        compliance.is_deleted = True
        compliance.updated_by_user_id = user_id
        db.commit()
        
        ComplianceService.log_history(
            db, tenant_id, compliance_id, "DELETED",
            None, None, user_id, "Compliance record deleted"
        )
        
        return True

    @staticmethod
    def get_compliance_summary(db: Session, tenant_id: int) -> dict:
        """Get compliance summary for dashboard"""
        compliances = db.query(Compliance).filter(
            and_(
                Compliance.tenant_id == tenant_id,
                Compliance.is_deleted == False
            )
        ).all()

        total = len(compliances)
        active = len([c for c in compliances if c.status == "ACTIVE"])
        pending = len([c for c in compliances if c.compliance_status == "PENDING"])
        compliant = len([c for c in compliances if c.compliance_status == "COMPLIANT"])
        non_compliant = len([c for c in compliances if c.compliance_status == "NON_COMPLIANT"])
        
        # Count upcoming filings (within 30 days)
        today = date.today()
        upcoming = len([c for c in compliances if c.next_filing_date and 
                       today <= c.next_filing_date <= today + timedelta(days=30)])

        return {
            "total_compliances": total,
            "active_compliances": active,
            "pending_compliances": pending,
            "compliant_count": compliant,
            "non_compliant_count": non_compliant,
            "upcoming_filings": upcoming
        }

    @staticmethod
    def log_history(db: Session, tenant_id: int, compliance_id: int, action: str,
                   field_name: Optional[str], old_value: Optional[str], 
                   user_id: int, change_reason: Optional[str] = None) -> ComplianceHistory:
        """Log compliance change in history"""
        history = ComplianceHistory(
            compliance_id=compliance_id,
            tenant_id=tenant_id,
            action=action,
            field_name=field_name,
            old_value=old_value,
            changed_by_user_id=user_id,
            change_reason=change_reason
        )
        db.add(history)
        db.commit()
        return history


# ─── Compliance Task Service ────────────────────────────────────────────────

class ComplianceTaskService:
    """Service for compliance task operations"""

    @staticmethod
    def create_compliance_task(db: Session, tenant_id: int, task_data: ComplianceTaskCreate, 
                              user_id: int) -> ComplianceTask:
        """Create a new compliance task"""
        compliance_task = ComplianceTask(
            compliance_id=task_data.compliance_id,
            task_id=task_data.task_id,
            tenant_id=tenant_id,
            assigned_to_user_id=task_data.assigned_to_user_id,
            assigned_by_user_id=task_data.assigned_by_user_id or user_id,
            task_type=task_data.task_type,
            description=task_data.description,
            due_date=task_data.due_date,
            status=task_data.status,
            completion_percentage=task_data.completion_percentage,
            compliance_requirement=task_data.compliance_requirement,
            documents_required=task_data.documents_required,
            documents_submitted_json=task_data.documents_submitted_json
        )
        db.add(compliance_task)
        db.commit()
        db.refresh(compliance_task)
        return compliance_task

    @staticmethod
    def get_compliance_task(db: Session, tenant_id: int, compliance_task_id: int) -> Optional[ComplianceTask]:
        """Get compliance task by ID"""
        return db.query(ComplianceTask).filter(
            and_(
                ComplianceTask.compliance_task_id == compliance_task_id,
                ComplianceTask.tenant_id == tenant_id,
                ComplianceTask.is_deleted == False
            )
        ).first()

    @staticmethod
    def get_compliance_tasks(db: Session, tenant_id: int, compliance_id: int) -> List[ComplianceTask]:
        """Get all tasks for a compliance"""
        return db.query(ComplianceTask).filter(
            and_(
                ComplianceTask.compliance_id == compliance_id,
                ComplianceTask.tenant_id == tenant_id,
                ComplianceTask.is_deleted == False
            )
        ).order_by(desc(ComplianceTask.created_at)).all()

    @staticmethod
    def get_employee_compliance_tasks(db: Session, tenant_id: int, user_id: int) -> List[ComplianceTask]:
        """Get all compliance tasks assigned to an employee"""
        return db.query(ComplianceTask).filter(
            and_(
                ComplianceTask.assigned_to_user_id == user_id,
                ComplianceTask.tenant_id == tenant_id,
                ComplianceTask.is_deleted == False
            )
        ).order_by(desc(ComplianceTask.due_date)).all()

    @staticmethod
    def update_compliance_task(db: Session, tenant_id: int, compliance_task_id: int,
                              task_data: ComplianceTaskUpdate) -> Optional[ComplianceTask]:
        """Update compliance task"""
        compliance_task = ComplianceTaskService.get_compliance_task(db, tenant_id, compliance_task_id)
        if not compliance_task:
            return None

        update_data = task_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(compliance_task, field, value)

        db.commit()
        db.refresh(compliance_task)
        return compliance_task

    @staticmethod
    def submit_compliance_task(db: Session, tenant_id: int, compliance_task_id: int,
                              documents: Optional[dict] = None) -> Optional[ComplianceTask]:
        """Submit compliance task with documents"""
        compliance_task = ComplianceTaskService.get_compliance_task(db, tenant_id, compliance_task_id)
        if not compliance_task:
            return None

        compliance_task.status = "SUBMITTED"
        compliance_task.completion_percentage = 100
        compliance_task.documents_submitted_json = documents
        db.commit()
        db.refresh(compliance_task)
        return compliance_task

    @staticmethod
    def approve_compliance_task(db: Session, tenant_id: int, compliance_task_id: int,
                               reviewer_id: int, comments: Optional[str] = None) -> Optional[ComplianceTask]:
        """Approve compliance task"""
        compliance_task = ComplianceTaskService.get_compliance_task(db, tenant_id, compliance_task_id)
        if not compliance_task:
            return None

        compliance_task.status = "APPROVED"
        compliance_task.reviewed_by_user_id = reviewer_id
        compliance_task.reviewed_date = date.today()
        compliance_task.review_comments = comments
        db.commit()
        db.refresh(compliance_task)
        return compliance_task

    @staticmethod
    def reject_compliance_task(db: Session, tenant_id: int, compliance_task_id: int,
                              reviewer_id: int, comments: Optional[str] = None) -> Optional[ComplianceTask]:
        """Reject compliance task"""
        compliance_task = ComplianceTaskService.get_compliance_task(db, tenant_id, compliance_task_id)
        if not compliance_task:
            return None

        compliance_task.status = "REJECTED"
        compliance_task.reviewed_by_user_id = reviewer_id
        compliance_task.reviewed_date = date.today()
        compliance_task.review_comments = comments
        db.commit()
        db.refresh(compliance_task)
        return compliance_task

    @staticmethod
    def get_compliance_task_summary(db: Session, tenant_id: int) -> dict:
        """Get compliance task summary"""
        tasks = db.query(ComplianceTask).filter(
            and_(
                ComplianceTask.tenant_id == tenant_id,
                ComplianceTask.is_deleted == False
            )
        ).all()

        total = len(tasks)
        assigned = len([t for t in tasks if t.status == "ASSIGNED"])
        in_progress = len([t for t in tasks if t.status == "IN_PROGRESS"])
        completed = len([t for t in tasks if t.status == "COMPLETED"])
        pending_review = len([t for t in tasks if t.status == "SUBMITTED"])
        
        # Count overdue tasks
        today = date.today()
        overdue = len([t for t in tasks if t.due_date < today and t.status not in ["COMPLETED", "APPROVED"]])

        return {
            "total_tasks": total,
            "assigned_tasks": assigned,
            "in_progress_tasks": in_progress,
            "completed_tasks": completed,
            "pending_review_tasks": pending_review,
            "overdue_tasks": overdue
        }


# ─── Compliance Reminder Service ────────────────────────────────────────────

class ComplianceReminderService:
    """Service for compliance reminder operations"""

    @staticmethod
    def create_reminder(db: Session, tenant_id: int, reminder_data: ComplianceReminderCreate) -> ComplianceReminder:
        """Create a new compliance reminder"""
        reminder = ComplianceReminder(
            compliance_id=reminder_data.compliance_id,
            tenant_id=tenant_id,
            reminder_type=reminder_data.reminder_type,
            reminder_date=reminder_data.reminder_date,
            days_before_due=reminder_data.days_before_due,
            notify_user_ids=reminder_data.notify_user_ids,
            notification_channels=reminder_data.notification_channels
        )
        db.add(reminder)
        db.commit()
        db.refresh(reminder)
        return reminder

    @staticmethod
    def get_pending_reminders(db: Session, tenant_id: int) -> List[ComplianceReminder]:
        """Get all pending reminders for today"""
        today = date.today()
        return db.query(ComplianceReminder).filter(
            and_(
                ComplianceReminder.tenant_id == tenant_id,
                ComplianceReminder.reminder_date <= today,
                ComplianceReminder.status == "PENDING"
            )
        ).all()

    @staticmethod
    def mark_reminder_sent(db: Session, reminder_id: int) -> Optional[ComplianceReminder]:
        """Mark reminder as sent"""
        reminder = db.query(ComplianceReminder).filter(
            ComplianceReminder.reminder_id == reminder_id
        ).first()
        
        if reminder:
            reminder.status = "SENT"
            reminder.sent_at = datetime.now()
            db.commit()
            db.refresh(reminder)
        
        return reminder

    @staticmethod
    def acknowledge_reminder(db: Session, reminder_id: int) -> Optional[ComplianceReminder]:
        """Acknowledge reminder"""
        reminder = db.query(ComplianceReminder).filter(
            ComplianceReminder.reminder_id == reminder_id
        ).first()
        
        if reminder:
            reminder.status = "ACKNOWLEDGED"
            reminder.acknowledged_at = datetime.now()
            db.commit()
            db.refresh(reminder)
        
        return reminder
