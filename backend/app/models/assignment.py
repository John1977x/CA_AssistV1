from sqlalchemy import (
    Boolean, Column, Date, DateTime, ForeignKey,
    Integer, String, Text, func, ARRAY, Numeric
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.db.session import Base


class AssignmentTemplate(Base):
    """Pre-defined assignment templates (15 predefined ones)"""
    __tablename__ = "assignment_template"

    template_id         = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id           = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False)
    title               = Column(String(200), nullable=False)
    description         = Column(Text)
    category            = Column(String(50), nullable=False)  # e.g., GST, ITR, AUDIT, etc.
    total_steps         = Column(Integer, nullable=False, default=1)
    estimated_hours     = Column(Numeric(6, 2))
    difficulty_level    = Column(String(20), nullable=False, default="MEDIUM")  # EASY, MEDIUM, HARD
    is_active           = Column(Boolean, nullable=False, default=True)
    created_at          = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at          = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    tenant              = relationship("Tenant")
    steps               = relationship("AssignmentTemplateStep", back_populates="template", cascade="all, delete-orphan")
    assignments         = relationship("Assignment", back_populates="template")


class AssignmentTemplateStep(Base):
    """Steps within an assignment template"""
    __tablename__ = "assignment_template_step"

    step_id             = Column(Integer, primary_key=True, autoincrement=True)
    template_id         = Column(Integer, ForeignKey("assignment_template.template_id"), nullable=False)
    step_number         = Column(Integer, nullable=False)
    title               = Column(String(200), nullable=False)
    description         = Column(Text)
    instructions        = Column(Text)
    estimated_hours     = Column(Numeric(6, 2))
    is_required         = Column(Boolean, nullable=False, default=True)
    created_at          = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    template            = relationship("AssignmentTemplate", back_populates="steps")
    submissions         = relationship("AssignmentStepSubmission", back_populates="step")


class Assignment(Base):
    """Assignments assigned to employees"""
    __tablename__ = "assignment"

    assignment_id       = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id           = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False)
    template_id         = Column(Integer, ForeignKey("assignment_template.template_id"), nullable=False)
    assigned_to_user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    assigned_by_user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    title               = Column(String(200), nullable=False)
    description         = Column(Text)
    due_date            = Column(Date, nullable=False)
    status              = Column(String(30), nullable=False, default="ASSIGNED")  # ASSIGNED, IN_PROGRESS, SUBMITTED, APPROVED, REJECTED
    completion_percentage = Column(Integer, nullable=False, default=0)
    total_score         = Column(Numeric(5, 2))
    feedback            = Column(Text)
    created_at          = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at          = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    submitted_at        = Column(DateTime(timezone=True))
    approved_at         = Column(DateTime(timezone=True))
    approved_by_user_id = Column(Integer, ForeignKey("user.user_id"))

    tenant              = relationship("Tenant")
    template            = relationship("AssignmentTemplate", back_populates="assignments")
    assigned_to         = relationship("User", foreign_keys=[assigned_to_user_id])
    assigned_by         = relationship("User", foreign_keys=[assigned_by_user_id])
    approved_by         = relationship("User", foreign_keys=[approved_by_user_id])
    step_submissions    = relationship("AssignmentStepSubmission", back_populates="assignment", cascade="all, delete-orphan")


class AssignmentStepSubmission(Base):
    """Employee submissions for each step"""
    __tablename__ = "assignment_step_submission"

    submission_id       = Column(Integer, primary_key=True, autoincrement=True)
    assignment_id       = Column(Integer, ForeignKey("assignment.assignment_id"), nullable=False)
    step_id             = Column(Integer, ForeignKey("assignment_template_step.step_id"), nullable=False)
    submitted_by_user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    status              = Column(String(30), nullable=False, default="PENDING")  # PENDING, APPROVED, REJECTED
    submission_text     = Column(Text)
    file_url            = Column(String(500))
    file_name           = Column(String(200))
    file_size           = Column(Integer)
    mime_type           = Column(String(100))
    score               = Column(Numeric(5, 2))
    feedback            = Column(Text)
    submitted_at        = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    reviewed_at         = Column(DateTime(timezone=True))
    reviewed_by_user_id = Column(Integer, ForeignKey("user.user_id"))

    assignment          = relationship("Assignment", back_populates="step_submissions")
    step                = relationship("AssignmentTemplateStep", back_populates="submissions")
    submitted_by        = relationship("User", foreign_keys=[submitted_by_user_id])
    reviewed_by         = relationship("User", foreign_keys=[reviewed_by_user_id])
