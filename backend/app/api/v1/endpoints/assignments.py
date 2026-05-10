from fastapi import APIRouter, Depends, Query, Path, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import math

from app.db.session import get_db
from app.core.deps import get_current_active_user
from app.models.auth import User
from app.schemas.assignment import (
    AssignmentTemplateCreate, AssignmentTemplateOut,
    AssignmentCreate, AssignmentUpdate, AssignmentOut, AssignmentDetailOut,
    AssignmentStepSubmissionCreate, AssignmentStepSubmissionReview, AssignmentStepSubmissionOut,
    PaginatedResponse, MessageResponse,
)
from app.services import assignment as svc

router = APIRouter(prefix="/assignments", tags=["Assignments"])


# ─── Assignment Templates ────────────────────────────────────────────────────

@router.get("/templates", response_model=PaginatedResponse)
async def list_templates(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get all assignment templates"""
    templates, total = await svc.get_assignment_templates(
        db, current_user.tenant_id, page, page_size, category
    )
    return PaginatedResponse(
        items=[AssignmentTemplateOut.model_validate(t) for t in templates],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total else 1,
    )


@router.get("/templates/{template_id}", response_model=AssignmentTemplateOut)
async def get_template(
    template_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific assignment template"""
    template = await svc.get_assignment_template(db, current_user.tenant_id, template_id)
    return AssignmentTemplateOut.model_validate(template)


@router.post("/templates", response_model=AssignmentTemplateOut, status_code=201)
async def create_template(
    data: AssignmentTemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new assignment template"""
    template = await svc.create_assignment_template(db, current_user.tenant_id, data)
    return AssignmentTemplateOut.model_validate(template)


# ─── Assignments ─────────────────────────────────────────────────────────────

@router.get("", response_model=PaginatedResponse)
async def list_assignments(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    assigned_to_user_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get assignments"""
    assignments, total = await svc.get_assignments(
        db, current_user.tenant_id, page, page_size, assigned_to_user_id, status
    )
    return PaginatedResponse(
        items=[AssignmentOut.model_validate(a) for a in assignments],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total else 1,
    )


@router.get("/{assignment_id}", response_model=AssignmentDetailOut)
async def get_assignment(
    assignment_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific assignment with all step submissions"""
    assignment = await svc.get_assignment(db, current_user.tenant_id, assignment_id)
    return AssignmentDetailOut.model_validate(assignment)


@router.post("", response_model=AssignmentOut, status_code=201)
async def create_assignment(
    data: AssignmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Assign an assignment to an employee"""
    assignment = await svc.create_assignment(
        db, current_user.tenant_id, current_user.user_id, data
    )
    return AssignmentOut.model_validate(assignment)


@router.patch("/{assignment_id}", response_model=AssignmentOut)
async def update_assignment(
    data: AssignmentUpdate,
    assignment_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update assignment status and feedback"""
    assignment = await svc.update_assignment(db, current_user.tenant_id, assignment_id, data)
    return AssignmentOut.model_validate(assignment)


# ─── Step Submissions ────────────────────────────────────────────────────────

@router.post("/{assignment_id}/steps/{step_id}/submit", response_model=AssignmentStepSubmissionOut, status_code=201)
async def submit_step(
    data: AssignmentStepSubmissionCreate,
    assignment_id: int = Path(...),
    step_id: int = Path(...),
    file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Submit a step for an assignment"""
    file_url = None
    file_name = None
    file_size = None
    mime_type = None

    if file:
        # TODO: Implement file upload to cloud storage (S3, GCS, etc.)
        # For now, store file metadata
        file_name = file.filename
        file_size = file.size
        mime_type = file.content_type
        # file_url would be set after uploading to cloud storage

    submission = await svc.submit_step(
        db, current_user.tenant_id, assignment_id, step_id, current_user.user_id,
        data, file_url, file_name, file_size, mime_type
    )
    return AssignmentStepSubmissionOut.model_validate(submission)


@router.patch("/{assignment_id}/submissions/{submission_id}/review", response_model=AssignmentStepSubmissionOut)
async def review_submission(
    data: AssignmentStepSubmissionReview,
    assignment_id: int = Path(...),
    submission_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Review and score a step submission (Manager only)"""
    submission = await svc.review_step_submission(
        db, current_user.tenant_id, submission_id, current_user.user_id, data
    )
    return AssignmentStepSubmissionOut.model_validate(submission)


@router.get("/{assignment_id}/submissions", response_model=list)
async def get_submissions(
    assignment_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get all step submissions for an assignment"""
    submissions = await svc.get_step_submissions(db, assignment_id)
    return [AssignmentStepSubmissionOut.model_validate(s) for s in submissions]
