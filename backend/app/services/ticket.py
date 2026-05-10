from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, or_, and_
from fastapi import HTTPException
from datetime import datetime, timezone
from typing import Optional, List, Tuple

from app.models.ticket import Ticket, TicketComment
from app.schemas.ticket import TicketCreate, TicketUpdate, TicketCommentCreate


async def _generate_ticket_number(db: AsyncSession, tenant_id: int) -> str:
    """Generate unique ticket number"""
    result = await db.execute(
        select(func.count(Ticket.ticket_id)).where(
            Ticket.tenant_id == tenant_id,
            Ticket.is_deleted == False,
        )
    )
    count = result.scalar() or 0
    return f"TKT-{str(count + 1).zfill(5)}"


async def get_tickets(
    db: AsyncSession,
    tenant_id: int,
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    assigned_to_user_id: Optional[int] = None,
    customer_id: Optional[int] = None,
) -> Tuple[List[Ticket], int]:
    """Get tickets with filters"""
    query = select(Ticket).where(
        Ticket.tenant_id == tenant_id,
        Ticket.is_deleted == False,
    )

    if status:
        query = query.where(Ticket.status == status)
    if priority:
        query = query.where(Ticket.priority == priority)
    if category:
        query = query.where(Ticket.category == category)
    if assigned_to_user_id:
        query = query.where(Ticket.assigned_to_user_id == assigned_to_user_id)
    if customer_id:
        query = query.where(Ticket.customer_id == customer_id)
    if search:
        query = query.where(
            or_(
                Ticket.title.ilike(f"%{search}%"),
                Ticket.description.ilike(f"%{search}%"),
                Ticket.ticket_number.ilike(f"%{search}%"),
            )
        )

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()

    query = (
        query
        .offset((page - 1) * page_size)
        .limit(page_size)
        .order_by(Ticket.created_at.desc())
    )
    result = await db.execute(query)
    return result.scalars().all(), total


async def get_ticket(db: AsyncSession, tenant_id: int, ticket_id: int) -> Ticket:
    """Get specific ticket"""
    result = await db.execute(
        select(Ticket).where(
            Ticket.ticket_id == ticket_id,
            Ticket.tenant_id == tenant_id,
            Ticket.is_deleted == False,
        )
    )
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found.")
    return ticket


async def create_ticket(
    db: AsyncSession,
    tenant_id: int,
    customer_id: int,
    user_id: int,
    data: TicketCreate,
) -> Ticket:
    """Create new ticket"""
    ticket_number = await _generate_ticket_number(db, tenant_id)

    ticket = Ticket(
        tenant_id=tenant_id,
        customer_id=customer_id,
        raised_by_user_id=user_id,
        ticket_number=ticket_number,
        title=data.title,
        description=data.description,
        category=data.category,
        priority=data.priority or "MEDIUM",
        status="OPEN",
        tags=data.tags,
    )
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)
    return ticket


async def update_ticket(
    db: AsyncSession,
    tenant_id: int,
    ticket_id: int,
    data: TicketUpdate,
) -> Ticket:
    """Update ticket"""
    ticket = await get_ticket(db, tenant_id, ticket_id)

    update_data = data.model_dump(exclude_unset=True)
    
    # Handle status changes
    if "status" in update_data:
        if update_data["status"] == "RESOLVED":
            update_data["resolved_at"] = datetime.now(timezone.utc)
        elif update_data["status"] == "CLOSED":
            update_data["closed_at"] = datetime.now(timezone.utc)

    if update_data:
        await db.execute(
            update(Ticket)
            .where(Ticket.ticket_id == ticket_id)
            .values(**update_data)
        )
        await db.commit()
        await db.refresh(ticket)

    return ticket


async def close_ticket(
    db: AsyncSession,
    tenant_id: int,
    ticket_id: int,
    resolution: str,
    resolved_by_user_id: int,
) -> Ticket:
    """Close ticket with resolution"""
    ticket = await get_ticket(db, tenant_id, ticket_id)

    await db.execute(
        update(Ticket)
        .where(Ticket.ticket_id == ticket_id)
        .values(
            status="CLOSED",
            resolution=resolution,
            resolved_by_user_id=resolved_by_user_id,
            resolved_at=datetime.now(timezone.utc),
            closed_at=datetime.now(timezone.utc),
        )
    )
    await db.commit()
    await db.refresh(ticket)
    return ticket


async def add_comment(
    db: AsyncSession,
    tenant_id: int,
    ticket_id: int,
    user_id: int,
    data: TicketCommentCreate,
) -> TicketComment:
    """Add comment to ticket"""
    # Verify ticket exists
    await get_ticket(db, tenant_id, ticket_id)

    comment = TicketComment(
        ticket_id=ticket_id,
        user_id=user_id,
        comment_text=data.comment_text,
        is_internal=data.is_internal,
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment


async def get_ticket_comments(
    db: AsyncSession,
    ticket_id: int,
    include_internal: bool = False,
) -> List[TicketComment]:
    """Get comments for ticket"""
    query = select(TicketComment).where(TicketComment.ticket_id == ticket_id)
    
    if not include_internal:
        query = query.where(TicketComment.is_internal == False)
    
    query = query.order_by(TicketComment.created_at.asc())
    result = await db.execute(query)
    return result.scalars().all()


async def get_ticket_stats(db: AsyncSession, tenant_id: int) -> dict:
    """Get ticket statistics"""
    total_q = await db.execute(
        select(func.count(Ticket.ticket_id)).where(
            Ticket.tenant_id == tenant_id,
            Ticket.is_deleted == False,
        )
    )
    open_q = await db.execute(
        select(func.count(Ticket.ticket_id)).where(
            Ticket.tenant_id == tenant_id,
            Ticket.is_deleted == False,
            Ticket.status == "OPEN",
        )
    )
    in_progress_q = await db.execute(
        select(func.count(Ticket.ticket_id)).where(
            Ticket.tenant_id == tenant_id,
            Ticket.is_deleted == False,
            Ticket.status == "IN_PROGRESS",
        )
    )
    resolved_q = await db.execute(
        select(func.count(Ticket.ticket_id)).where(
            Ticket.tenant_id == tenant_id,
            Ticket.is_deleted == False,
            Ticket.status == "RESOLVED",
        )
    )
    urgent_q = await db.execute(
        select(func.count(Ticket.ticket_id)).where(
            Ticket.tenant_id == tenant_id,
            Ticket.is_deleted == False,
            Ticket.priority == "URGENT",
        )
    )

    return {
        "total": total_q.scalar() or 0,
        "open": open_q.scalar() or 0,
        "in_progress": in_progress_q.scalar() or 0,
        "resolved": resolved_q.scalar() or 0,
        "urgent": urgent_q.scalar() or 0,
    }
