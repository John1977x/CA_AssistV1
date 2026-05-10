from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal


# ─── Assignment Template Schemas ──────────────────────────────────────────────

class AssignmentTemplateStepCreate(BaseModel):
    step_number: int
    title: str
    description: Optional[str] = None
    instructions: Optional[str] = None
    estimated_hours: Optional[Decimal] = None
    is_required: bool = True


class AssignmentTemplateStepOut(AssignmentTemplateStepCreate):
    step_id: int

    class Config:
        from_attributes = True


class AssignmentTemplateCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category: str
    total_steps: int = 1
    estimated_hours: Optional[Decimal] = None
    difficulty_level: str = "MEDIUM"
    steps: List[AssignmentTemplateStepCreate] = []


class AssignmentTemplateUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    difficulty_level: Optional[str] = None
    is_active: Optional[bool] = None


class AssignmentTemplateOut(BaseModel):
    template_id: int
    title: str
    description: Optional[str]
    category: str
    total_steps: int
    estimated_hours: Optional[Decimal]
    difficulty_level: str
    is_active: bool
    steps: List[AssignmentTemplateStepOut]
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Assignment Schemas ──────────────────────────────────────────────────────

class AssignmentCreate(BaseModel):
    template_id: int
    assigned_to_user_id: int
    due_date: date
    title: Optional[str] = None
    description: Optional[str] = None


class AssignmentUpdate(BaseModel):
    status: Optional[str] = None
    feedback: Optional[str] = None
    total_score: Optional[Decimal] = None


class AssignmentOut(BaseModel):
    assignment_id: int
    template_id: int
    title: str
    description: Optional[str]
    assigned_to_user_id: int
    assigned_by_user_id: int
    due_date: date
    status: str
    completion_percentage: int
    total_score: Optional[Decimal]
    feedback: Optional[str]
    created_at: datetime
    submitted_at: Optional[datetime]
    approved_at: Optional[datetime]

    class Config:
        from_attributes = True


class AssignmentDetailOut(AssignmentOut):
    template: AssignmentTemplateOut
    step_submissions: List['AssignmentStepSubmissionOut'] = []


# ─── Step Submission Schemas ─────────────────────────────────────────────────

class AssignmentStepSubmissionCreate(BaseModel):
    submission_text: Optional[str] = None


class AssignmentStepSubmissionReview(BaseModel):
    status: str  # APPROVED or REJECTED
    score: Decimal
    feedback: Optional[str] = None


class AssignmentStepSubmissionOut(BaseModel):
    submission_id: int
    assignment_id: int
    step_id: int
    status: str
    submission_text: Optional[str]
    file_url: Optional[str]
    file_name: Optional[str]
    score: Optional[Decimal]
    feedback: Optional[str]
    submitted_at: datetime
    reviewed_at: Optional[datetime]

    class Config:
        from_attributes = True


# ─── Pagination ──────────────────────────────────────────────────────────────

class PaginatedResponse(BaseModel):
    items: List
    total: int
    page: int
    page_size: int
    total_pages: int


class MessageResponse(BaseModel):
    message: str
