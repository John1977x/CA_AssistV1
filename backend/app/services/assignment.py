from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, and_
from fastapi import HTTPException
from datetime import datetime, timezone
from typing import Optional, List, Tuple
from decimal import Decimal

from app.models.assignment import (
    AssignmentTemplate, AssignmentTemplateStep, Assignment, AssignmentStepSubmission
)
from app.schemas.assignment import (
    AssignmentTemplateCreate, AssignmentCreate, AssignmentUpdate,
    AssignmentStepSubmissionCreate, AssignmentStepSubmissionReview
)


# ─── Assignment Template CRUD ─────────────────────────────────────────────────

async def get_assignment_templates(
    db: AsyncSession,
    tenant_id: int,
    page: int = 1,
    page_size: int = 20,
    category: Optional[str] = None,
    is_active: bool = True,
) -> Tuple[List[AssignmentTemplate], int]:
    """Get all assignment templates"""
    query = select(AssignmentTemplate).where(
        AssignmentTemplate.tenant_id == tenant_id,
        AssignmentTemplate.is_active == is_active,
    )

    if category:
        query = query.where(AssignmentTemplate.category == category)

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()

    query = (
        query
        .offset((page - 1) * page_size)
        .limit(page_size)
        .order_by(AssignmentTemplate.created_at.desc())
    )
    result = await db.execute(query)
    return result.scalars().all(), total


async def get_assignment_template(
    db: AsyncSession, tenant_id: int, template_id: int
) -> AssignmentTemplate:
    """Get a specific assignment template"""
    result = await db.execute(
        select(AssignmentTemplate).where(
            AssignmentTemplate.template_id == template_id,
            AssignmentTemplate.tenant_id == tenant_id,
        )
    )
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=404, detail="Assignment template not found.")
    return template


async def create_assignment_template(
    db: AsyncSession, tenant_id: int, data: AssignmentTemplateCreate
) -> AssignmentTemplate:
    """Create a new assignment template"""
    template = AssignmentTemplate(
        tenant_id=tenant_id,
        title=data.title,
        description=data.description,
        category=data.category,
        total_steps=data.total_steps,
        estimated_hours=data.estimated_hours,
        difficulty_level=data.difficulty_level,
    )
    db.add(template)
    await db.flush()

    # Add steps
    for step_data in data.steps:
        step = AssignmentTemplateStep(
            template_id=template.template_id,
            step_number=step_data.step_number,
            title=step_data.title,
            description=step_data.description,
            instructions=step_data.instructions,
            estimated_hours=step_data.estimated_hours,
            is_required=step_data.is_required,
        )
        db.add(step)

    await db.commit()
    await db.refresh(template)
    return template


# ─── Assignment CRUD ─────────────────────────────────────────────────────────

async def get_assignments(
    db: AsyncSession,
    tenant_id: int,
    page: int = 1,
    page_size: int = 20,
    assigned_to_user_id: Optional[int] = None,
    status: Optional[str] = None,
) -> Tuple[List[Assignment], int]:
    """Get assignments"""
    query = select(Assignment).where(
        Assignment.tenant_id == tenant_id,
    )

    if assigned_to_user_id:
        query = query.where(Assignment.assigned_to_user_id == assigned_to_user_id)
    if status:
        query = query.where(Assignment.status == status)

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()

    query = (
        query
        .offset((page - 1) * page_size)
        .limit(page_size)
        .order_by(Assignment.due_date.asc(), Assignment.created_at.desc())
    )
    result = await db.execute(query)
    return result.scalars().all(), total


async def get_assignment(
    db: AsyncSession, tenant_id: int, assignment_id: int
) -> Assignment:
    """Get a specific assignment"""
    result = await db.execute(
        select(Assignment).where(
            Assignment.assignment_id == assignment_id,
            Assignment.tenant_id == tenant_id,
        )
    )
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found.")
    return assignment


async def create_assignment(
    db: AsyncSession, tenant_id: int, assigned_by_user_id: int, data: AssignmentCreate
) -> Assignment:
    """Create and assign an assignment to an employee"""
    # Verify template exists
    template = await get_assignment_template(db, tenant_id, data.template_id)

    assignment = Assignment(
        tenant_id=tenant_id,
        template_id=data.template_id,
        assigned_to_user_id=data.assigned_to_user_id,
        assigned_by_user_id=assigned_by_user_id,
        title=data.title or template.title,
        description=data.description or template.description,
        due_date=data.due_date,
        status="ASSIGNED",
    )
    db.add(assignment)
    await db.commit()
    await db.refresh(assignment)
    return assignment


async def update_assignment(
    db: AsyncSession, tenant_id: int, assignment_id: int, data: AssignmentUpdate
) -> Assignment:
    """Update assignment status and feedback"""
    assignment = await get_assignment(db, tenant_id, assignment_id)

    update_data = data.model_dump(exclude_unset=True)
    if update_data:
        await db.execute(
            update(Assignment)
            .where(Assignment.assignment_id == assignment_id)
            .values(**update_data)
        )
        await db.commit()
        await db.refresh(assignment)

    return assignment


# ─── Step Submission ──────────────────────────────────────────────────────────

async def submit_step(
    db: AsyncSession,
    tenant_id: int,
    assignment_id: int,
    step_id: int,
    user_id: int,
    data: AssignmentStepSubmissionCreate,
    file_url: Optional[str] = None,
    file_name: Optional[str] = None,
    file_size: Optional[int] = None,
    mime_type: Optional[str] = None,
) -> AssignmentStepSubmission:
    """Submit a step for an assignment"""
    # Verify assignment exists
    assignment = await get_assignment(db, tenant_id, assignment_id)

    # Check if submission already exists
    existing = await db.execute(
        select(AssignmentStepSubmission).where(
            AssignmentStepSubmission.assignment_id == assignment_id,
            AssignmentStepSubmission.step_id == step_id,
        )
    )
    existing_submission = existing.scalar_one_or_none()

    if existing_submission:
        # Update existing submission
        await db.execute(
            update(AssignmentStepSubmission)
            .where(AssignmentStepSubmission.submission_id == existing_submission.submission_id)
            .values(
                submission_text=data.submission_text,
                file_url=file_url,
                file_name=file_name,
                file_size=file_size,
                mime_type=mime_type,
                submitted_at=datetime.now(timezone.utc),
                status="PENDING",
            )
        )
        await db.commit()
        await db.refresh(existing_submission)
        return existing_submission

    # Create new submission
    submission = AssignmentStepSubmission(
        assignment_id=assignment_id,
        step_id=step_id,
        submitted_by_user_id=user_id,
        submission_text=data.submission_text,
        file_url=file_url,
        file_name=file_name,
        file_size=file_size,
        mime_type=mime_type,
        status="PENDING",
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)
    return submission


async def review_step_submission(
    db: AsyncSession,
    tenant_id: int,
    submission_id: int,
    reviewer_user_id: int,
    data: AssignmentStepSubmissionReview,
) -> AssignmentStepSubmission:
    """Review and score a step submission"""
    result = await db.execute(
        select(AssignmentStepSubmission).where(
            AssignmentStepSubmission.submission_id == submission_id,
        )
    )
    submission = result.scalar_one_or_none()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found.")

    # Update submission
    await db.execute(
        update(AssignmentStepSubmission)
        .where(AssignmentStepSubmission.submission_id == submission_id)
        .values(
            status=data.status,
            score=data.score,
            feedback=data.feedback,
            reviewed_at=datetime.now(timezone.utc),
            reviewed_by_user_id=reviewer_user_id,
        )
    )

    # Update assignment completion percentage and status
    assignment = await get_assignment(db, tenant_id, submission.assignment_id)
    
    # Get all submissions for this assignment
    submissions_result = await db.execute(
        select(AssignmentStepSubmission).where(
            AssignmentStepSubmission.assignment_id == submission.assignment_id,
        )
    )
    all_submissions = submissions_result.scalars().all()

    # Calculate completion percentage
    approved_count = sum(1 for s in all_submissions if s.status == "APPROVED")
    total_count = len(all_submissions)
    completion_percentage = int((approved_count / total_count * 100)) if total_count > 0 else 0

    # Calculate total score
    total_score = sum(s.score or 0 for s in all_submissions if s.status == "APPROVED")

    # Update assignment
    new_status = "APPROVED" if completion_percentage == 100 else "IN_PROGRESS"
    await db.execute(
        update(Assignment)
        .where(Assignment.assignment_id == submission.assignment_id)
        .values(
            completion_percentage=completion_percentage,
            total_score=total_score,
            status=new_status,
            approved_at=datetime.now(timezone.utc) if new_status == "APPROVED" else None,
            approved_by_user_id=reviewer_user_id if new_status == "APPROVED" else None,
        )
    )

    await db.commit()
    await db.refresh(submission)
    return submission


async def get_step_submissions(
    db: AsyncSession,
    assignment_id: int,
) -> List[AssignmentStepSubmission]:
    """Get all step submissions for an assignment"""
    result = await db.execute(
        select(AssignmentStepSubmission).where(
            AssignmentStepSubmission.assignment_id == assignment_id,
        )
        .order_by(AssignmentStepSubmission.step_id.asc())
    )
    return result.scalars().all()
