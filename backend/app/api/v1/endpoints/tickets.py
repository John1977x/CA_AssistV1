from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.deps import get_db, get_current_user
from app.schemas.ticket import (
    TicketCreate, TicketUpdate, TicketOut, TicketDetailOut,
    TicketCommentCreate, TicketCommentOut, PaginatedResponse, MessageResponse
)
from app.services import ticket as ticket_service
from app.models.auth import User

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("", response_model=TicketOut)
async def create_ticket(
    data: TicketCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new support ticket (Client only)"""
    # Get customer_id from current user
    from app.models.customer import Customer
    from sqlalchemy import select
    
    result = await db.execute(
        select(Customer).where(Customer.email == current_user.email)
    )
    customer = result.scalar_one_or_none()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found.")
    
    ticket = await ticket_service.create_ticket(
        db=db,
        tenant_id=current_user.tenant_id,
        customer_id=customer.customer_id,
        user_id=current_user.user_id,
        data=data,
    )
    return ticket


@router.get("", response_model=PaginatedResponse)
async def list_tickets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List tickets (filtered by role)"""
    from app.models.company import CompanyUser
    from sqlalchemy import select
    
    # Check user role
    result = await db.execute(
        select(CompanyUser).where(
            CompanyUser.user_id == current_user.user_id
        )
    )
    company_user = result.scalar_one_or_none()
    
    if not company_user:
        raise HTTPException(status_code=403, detail="Not authorized.")
    
    role = company_user.role
    
    # Filter based on role
    if role == "CLIENT":
        # Clients see only their own tickets
        from app.models.customer import Customer
        result = await db.execute(
            select(Customer).where(Customer.email == current_user.email)
        )
        customer = result.scalar_one_or_none()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found.")
        customer_id = customer.customer_id
    else:
        # Owner, Manager, Employee see all tickets
        customer_id = None
    
    tickets, total = await ticket_service.get_tickets(
        db=db,
        tenant_id=current_user.tenant_id,
        page=page,
        page_size=page_size,
        status=status,
        priority=priority,
        category=category,
        search=search,
        customer_id=customer_id,
    )
    
    return PaginatedResponse(
        items=tickets,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/stats", response_model=dict)
async def get_ticket_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get ticket statistics"""
    stats = await ticket_service.get_ticket_stats(db, current_user.tenant_id)
    return stats


@router.get("/{ticket_id}", response_model=TicketDetailOut)
async def get_ticket(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get ticket details with comments"""
    from app.models.company import CompanyUser
    from sqlalchemy import select
    
    ticket = await ticket_service.get_ticket(db, current_user.tenant_id, ticket_id)
    
    # Check authorization
    result = await db.execute(
        select(CompanyUser).where(
            CompanyUser.user_id == current_user.user_id
        )
    )
    company_user = result.scalar_one_or_none()
    
    if not company_user:
        raise HTTPException(status_code=403, detail="Not authorized.")
    
    role = company_user.role
    
    if role == "CLIENT":
        # Clients can only see their own tickets
        from app.models.customer import Customer
        result = await db.execute(
            select(Customer).where(Customer.email == current_user.email)
        )
        customer = result.scalar_one_or_none()
        if not customer or ticket.customer_id != customer.customer_id:
            raise HTTPException(status_code=403, detail="Not authorized.")
    
    # Get comments
    comments = await ticket_service.get_ticket_comments(
        db, ticket_id, include_internal=(role != "CLIENT")
    )
    
    ticket_detail = TicketDetailOut.from_orm(ticket)
    ticket_detail.comments = comments
    return ticket_detail


@router.patch("/{ticket_id}", response_model=TicketOut)
async def update_ticket(
    ticket_id: int,
    data: TicketUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update ticket (Owner/Manager only)"""
    from app.models.company import CompanyUser
    from sqlalchemy import select
    
    # Check authorization
    result = await db.execute(
        select(CompanyUser).where(
            CompanyUser.user_id == current_user.user_id
        )
    )
    company_user = result.scalar_one_or_none()
    
    if not company_user or company_user.role not in ["OWNER", "MANAGER"]:
        raise HTTPException(status_code=403, detail="Not authorized.")
    
    ticket = await ticket_service.update_ticket(db, current_user.tenant_id, ticket_id, data)
    return ticket


@router.post("/{ticket_id}/close", response_model=TicketOut)
async def close_ticket(
    ticket_id: int,
    resolution: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Close ticket with resolution (Owner/Manager only)"""
    from app.models.company import CompanyUser
    from sqlalchemy import select
    
    # Check authorization
    result = await db.execute(
        select(CompanyUser).where(
            CompanyUser.user_id == current_user.user_id
        )
    )
    company_user = result.scalar_one_or_none()
    
    if not company_user or company_user.role not in ["OWNER", "MANAGER"]:
        raise HTTPException(status_code=403, detail="Not authorized.")
    
    ticket = await ticket_service.close_ticket(
        db, current_user.tenant_id, ticket_id, resolution, current_user.user_id
    )
    return ticket


@router.post("/{ticket_id}/comments", response_model=TicketCommentOut)
async def add_comment(
    ticket_id: int,
    data: TicketCommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add comment to ticket"""
    comment = await ticket_service.add_comment(
        db, current_user.tenant_id, ticket_id, current_user.user_id, data
    )
    return comment


@router.get("/{ticket_id}/comments", response_model=list[TicketCommentOut])
async def get_comments(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get ticket comments"""
    from app.models.company import CompanyUser
    from sqlalchemy import select
    
    # Check authorization
    result = await db.execute(
        select(CompanyUser).where(
            CompanyUser.user_id == current_user.user_id
        )
    )
    company_user = result.scalar_one_or_none()
    
    if not company_user:
        raise HTTPException(status_code=403, detail="Not authorized.")
    
    include_internal = company_user.role != "CLIENT"
    comments = await ticket_service.get_ticket_comments(db, ticket_id, include_internal)
    return comments
