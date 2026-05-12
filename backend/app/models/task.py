from sqlalchemy import (
    BigInteger, Boolean, Column, Date, DateTime, ForeignKey,
    Integer, Numeric, SmallInteger, String, Text, func, ARRAY
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
import uuid
from app.db.session import Base


class Task(Base):
    __tablename__ = "task"

    task_id                 = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id               = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False)
    customer_id             = Column(Integer, ForeignKey("customer.customer_id"), nullable=False)
    branch_id               = Column(Integer, ForeignKey("branch.branch_id"))
    assigned_to_user_id     = Column(Integer, ForeignKey("user.user_id"))
    reviewer_user_id        = Column(Integer, ForeignKey("user.user_id"))
    task_type_code          = Column(String(60), nullable=False)  # GSTR1, GSTR3B, ITR1, TDS_RETURN, ROC, AUDIT …
    task_title              = Column(String(300), nullable=False)
    description             = Column(Text)
    financial_year          = Column(String(7))    # 2024-25
    return_period           = Column(String(20))   # Apr-2024, Q1 2024-25
    due_date                = Column(Date, nullable=False)
    internal_due_date       = Column(Date)
    priority                = Column(String(10), nullable=False, default="MEDIUM")
    status                  = Column(String(30), nullable=False, default="PENDING")
    completion_percentage   = Column(SmallInteger, nullable=False, default=0)
    billing_status          = Column(String(20), nullable=False, default="UNBILLED")
    billed_amount           = Column(Numeric(10, 2))
    estimated_hours         = Column(Numeric(6, 2))
    actual_hours            = Column(Numeric(6, 2))
    acknowledgement_number  = Column(String(100))
    filed_at                = Column(DateTime(timezone=True))
    filed_by_user_id        = Column(Integer, ForeignKey("user.user_id"))
    parent_task_id          = Column(Integer, ForeignKey("task.task_id"))
    tags                    = Column(ARRAY(Text))
    created_at              = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at              = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    is_deleted              = Column(Boolean, nullable=False, default=False)

    tenant          = relationship("Tenant")
    customer        = relationship("Customer")
    branch          = relationship("Branch")
    assigned_to     = relationship("User", foreign_keys=[assigned_to_user_id])
    reviewer        = relationship("User", foreign_keys=[reviewer_user_id])
    filed_by        = relationship("User", foreign_keys=[filed_by_user_id])
    parent          = relationship("Task", remote_side="Task.task_id", foreign_keys=[parent_task_id])
    subtasks        = relationship("Task", foreign_keys=[parent_task_id], back_populates="parent")
    details         = relationship("TaskDetail", back_populates="task", cascade="all, delete-orphan", order_by="TaskDetail.step_order")
    reminders       = relationship("TaskReminder", back_populates="task", cascade="all, delete-orphan")


class TaskDetail(Base):
    __tablename__ = "task_detail"

    task_detail_id      = Column(Integer, primary_key=True, autoincrement=True)
    task_id             = Column(Integer, ForeignKey("task.task_id"), nullable=False)
    tenant_id           = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False)
    step_title          = Column(String(200), nullable=False)
    step_description    = Column(Text)
    step_order          = Column(Integer, nullable=False, default=0)
    assigned_to_user_id = Column(Integer, ForeignKey("user.user_id"))
    status              = Column(String(30), nullable=False, default="PENDING")
    is_required         = Column(Boolean, nullable=False, default=True)
    is_client_action    = Column(Boolean, nullable=False, default=False)
    due_date            = Column(Date)
    completed_at        = Column(DateTime(timezone=True))
    completed_by_user_id= Column(Integer, ForeignKey("user.user_id"))
    attachments_json    = Column(JSONB)
    notes_json          = Column(JSONB)
    form_data_json      = Column(JSONB)
    created_at          = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at          = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    task            = relationship("Task", back_populates="details")
    assigned_to     = relationship("User", foreign_keys=[assigned_to_user_id])
    completed_by    = relationship("User", foreign_keys=[completed_by_user_id])


class TaskReminder(Base):
    __tablename__ = "task_reminder"

    reminder_id         = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id           = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False)
    task_id             = Column(Integer, ForeignKey("task.task_id"), nullable=False)
    reminder_type       = Column(String(20), nullable=False)   # USER or CUSTOMER
    target_user_id      = Column(Integer, ForeignKey("user.user_id"))
    target_customer_id  = Column(Integer, ForeignKey("customer.customer_id"))
    channel             = Column(String(20), nullable=False)   # EMAIL, SMS, WHATSAPP, IN_APP, ALL
    subject             = Column(String(300))
    message_body        = Column(Text, nullable=False)
    template_code       = Column(String(60))
    scheduled_at        = Column(DateTime(timezone=True), nullable=False)
    sent_at             = Column(DateTime(timezone=True))
    delivery_status     = Column(String(20), nullable=False, default="PENDING")
    delivery_error      = Column(Text)
    retry_count         = Column(Integer, nullable=False, default=0)
    is_recurring        = Column(Boolean, nullable=False, default=False)
    recurrence_rule     = Column(String(100))
    is_acknowledged     = Column(Boolean, nullable=False, default=False)
    acknowledged_at     = Column(DateTime(timezone=True))
    created_by_user_id  = Column(Integer, ForeignKey("user.user_id"))
    created_at          = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    task            = relationship("Task", back_populates="reminders")
    target_user     = relationship("User", foreign_keys=[target_user_id])
    created_by      = relationship("User", foreign_keys=[created_by_user_id])
