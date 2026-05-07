"""
Company Management Endpoints for Multi-Company Architecture
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.auth import User
from app.models.company_v2 import (
    Company, CompanyBranch, CompanyRole, CompanyUser, CompanyClient,
    CompanyRoleEnum, UserStatusEnum
)
from app.schemas.auth_v2 import (
    CreateCompanyRequest, CompanyOut,
    AddTeamMemberRequest, TeamMemberOut,
    AddClientRequest, ClientOut,
    CreateBranchRequest, BranchOut,
    DocumentRequestTicketCreate, DocumentRequestTicketUpdate, DocumentRequestTicketOut,
)
from app.services.auth_v2 import (
    create_company, add_team_member, add_client, create_branch
)

router = APIRouter(prefix="/companies", tags=["Companies"])


# ─── Company Management ──────────────────────────────────────────────────────

@router.get("", response_model=List[CompanyOut])
async def list_companies(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
):
    """
    List all companies owned by current user (owner only)
    """
    if not current_user.is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners can list companies"
        )
    
    result = await db.execute(
        select(Company)
        .where(Company.owner_id == current_user.user_id)
        .offset(skip)
        .limit(limit)
    )
    companies = result.scalars().all()
    # Convert each company using from_orm to handle UUID serialization
    return [CompanyOut.from_orm(company) for company in companies]


@router.post("", response_model=CompanyOut, status_code=status.HTTP_201_CREATED)
async def create_company_endpoint(
    request: CreateCompanyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new company (owner only)
    """
    return await create_company(db, current_user.user_id, request)


@router.get("/{company_id}", response_model=CompanyOut)
async def get_company(
    company_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get company details
    """
    import uuid
    
    # Convert company_id to UUID
    try:
        company_uuid = uuid.UUID(company_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid company ID format"
        )
    
    result = await db.execute(
        select(Company).where(Company.company_id == company_uuid)
    )
    company = result.scalar_one_or_none()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Check if user has access
    company_user_result = await db.execute(
        select(CompanyUser).where(
            and_(
                CompanyUser.user_id == current_user.user_id,
                CompanyUser.company_id == company_uuid,
            )
        )
    )
    if not company_user_result.scalar_one_or_none() and company.owner_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this company"
        )
    
    return company


@router.patch("/{company_id}", response_model=CompanyOut)
async def update_company(
    company_id: str,
    request: CreateCompanyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update company details (owner only)
    """
    import uuid
    
    # Convert company_id to UUID
    try:
        company_uuid = uuid.UUID(company_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid company ID format"
        )
    
    result = await db.execute(
        select(Company).where(Company.company_id == company_uuid)
    )
    company = result.scalar_one_or_none()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    if company.owner_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owner can update company"
        )
    
    # Update fields
    company.company_name = request.company_name
    company.email = request.email
    company.phone = request.phone
    company.address_line1 = request.address_line1
    company.address_line2 = request.address_line2
    company.city = request.city
    company.state = request.state
    company.pincode = request.pincode
    company.pan = request.pan
    company.gstin = request.gstin
    company.cin = request.cin
    
    await db.commit()
    return company


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    company_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete company (owner only)
    """
    import uuid
    
    # Convert company_id to UUID
    try:
        company_uuid = uuid.UUID(company_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid company ID format"
        )
    
    result = await db.execute(
        select(Company).where(Company.company_id == company_uuid)
    )
    company = result.scalar_one_or_none()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    if company.owner_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owner can delete company"
        )
    
    company.is_deleted = True
    await db.commit()


# ─── Team Management ────────────────────────────────────────────────────────

@router.get("/{company_id}/team", response_model=List[TeamMemberOut])
async def list_team_members(
    company_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
):
    """
    List team members of a company
    """
    import uuid
    from sqlalchemy.orm import selectinload
    
    # Convert company_id to UUID
    try:
        company_uuid = uuid.UUID(company_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid company ID format"
        )
    
    # Verify user has access
    company_user_result = await db.execute(
        select(CompanyUser).where(
            and_(
                CompanyUser.user_id == current_user.user_id,
                CompanyUser.company_id == company_uuid,
            )
        )
    )
    if not company_user_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this company"
        )
    
    result = await db.execute(
        select(CompanyUser)
        .where(CompanyUser.company_id == company_uuid)
        .options(selectinload(CompanyUser.user), selectinload(CompanyUser.role))
        .offset(skip)
        .limit(limit)
    )
    team_members = result.scalars().all()
    # Convert each team member using from_orm to handle UUID serialization
    return [TeamMemberOut.from_orm(member) for member in team_members]


@router.post("/{company_id}/team/managers", response_model=TeamMemberOut, status_code=status.HTTP_201_CREATED)
async def add_manager(
    company_id: str,
    request: AddTeamMemberRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Add a manager to company
    """
    request.role = CompanyRoleEnum.MANAGER
    return await add_team_member(db, current_user.user_id, company_id, request)


@router.post("/{company_id}/team/employees", response_model=TeamMemberOut, status_code=status.HTTP_201_CREATED)
async def add_employee(
    company_id: str,
    request: AddTeamMemberRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Add an employee to company
    """
    request.role = CompanyRoleEnum.EMPLOYEE
    return await add_team_member(db, current_user.user_id, company_id, request)


@router.delete("/{company_id}/team/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_team_member(
    company_id: str,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Remove team member from company
    """
    import uuid
    
    # Convert company_id to UUID
    try:
        company_uuid = uuid.UUID(company_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid company ID format"
        )
    
    # Verify user has permission
    company_user_result = await db.execute(
        select(CompanyUser).where(
            and_(
                CompanyUser.user_id == current_user.user_id,
                CompanyUser.company_id == company_uuid,
            )
        )
    )
    company_user = company_user_result.scalar_one_or_none()
    
    if not company_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this company"
        )
    
    # Get role
    role_result = await db.execute(
        select(CompanyRole).where(CompanyRole.role_id == company_user.role_id)
    )
    role = role_result.scalar_one_or_none()
    
    if role.role_name not in [CompanyRoleEnum.OWNER, CompanyRoleEnum.MANAGER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to remove team members"
        )
    
    # Remove team member
    target_result = await db.execute(
        select(CompanyUser).where(
            and_(
                CompanyUser.user_id == user_id,
                CompanyUser.company_id == company_uuid,
            )
        )
    )
    target = target_result.scalar_one_or_none()
    
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team member not found"
        )
    
    target.is_deleted = True
    await db.commit()


# ─── Client Management ──────────────────────────────────────────────────────

@router.get("/{company_id}/clients", response_model=List[ClientOut])
async def list_clients(
    company_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
):
    """
    List clients of a company
    """
    import uuid
    
    # Convert company_id to UUID
    try:
        company_uuid = uuid.UUID(company_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid company ID format"
        )
    
    # Verify user has access
    company_user_result = await db.execute(
        select(CompanyUser).where(
            and_(
                CompanyUser.user_id == current_user.user_id,
                CompanyUser.company_id == company_uuid,
            )
        )
    )
    if not company_user_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this company"
        )
    
    result = await db.execute(
        select(CompanyClient)
        .where(CompanyClient.company_id == company_uuid)
        .offset(skip)
        .limit(limit)
    )
    clients = result.scalars().all()
    # Convert each client using from_orm to handle UUID serialization
    return [ClientOut.from_orm(client) for client in clients]


@router.post("/{company_id}/clients", response_model=ClientOut, status_code=status.HTTP_201_CREATED)
async def add_client_endpoint(
    company_id: str,
    request: AddClientRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Add a client to company
    """
    return await add_client(db, current_user.user_id, company_id, request)


@router.get("/{company_id}/clients/{client_id}", response_model=ClientOut)
async def get_client(
    company_id: str,
    client_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get client details
    """
    import uuid
    
    # Convert IDs to UUID
    try:
        company_uuid = uuid.UUID(company_id)
        client_uuid = uuid.UUID(client_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid company or client ID format"
        )
    
    result = await db.execute(
        select(CompanyClient).where(
            and_(
                CompanyClient.client_id == client_uuid,
                CompanyClient.company_id == company_uuid,
            )
        )
    )
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    return client


@router.delete("/{company_id}/clients/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    company_id: str,
    client_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete client
    """
    import uuid
    
    # Convert IDs to UUID
    try:
        company_uuid = uuid.UUID(company_id)
        client_uuid = uuid.UUID(client_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid company or client ID format"
        )
    
    result = await db.execute(
        select(CompanyClient).where(
            and_(
                CompanyClient.client_id == client_uuid,
                CompanyClient.company_id == company_uuid,
            )
        )
    )
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    client.is_deleted = True
    await db.commit()


# ─── Branch Management ──────────────────────────────────────────────────────

@router.get("/{company_id}/branches", response_model=List[BranchOut])
async def list_branches(
    company_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
):
    """
    List branches of a company
    """
    import uuid
    
    # Convert company_id string to UUID
    try:
        company_uuid = uuid.UUID(company_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid company ID format"
        )
    
    # Verify user has access to this company
    company_user_result = await db.execute(
        select(CompanyUser).where(
            and_(
                CompanyUser.user_id == current_user.user_id,
                CompanyUser.company_id == company_uuid,
            )
        )
    )
    if not company_user_result.scalar_one_or_none():
        # Also check if user is the owner of the company
        company_result = await db.execute(
            select(Company).where(Company.company_id == company_uuid)
        )
        company = company_result.scalar_one_or_none()
        if not company or company.owner_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this company"
            )
    
    result = await db.execute(
        select(CompanyBranch)
        .where(CompanyBranch.company_id == company_uuid)
        .offset(skip)
        .limit(limit)
    )
    branches = result.scalars().all()
    # Convert each branch using from_orm to handle UUID serialization
    return [BranchOut.from_orm(branch) for branch in branches]


@router.post("/{company_id}/branches", response_model=BranchOut, status_code=status.HTTP_201_CREATED)
async def create_branch_endpoint(
    company_id: str,
    request: CreateBranchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a branch for company
    """
    return await create_branch(db, current_user.user_id, company_id, request)


@router.get("/{company_id}/branches/{branch_id}", response_model=BranchOut)
async def get_branch(
    company_id: str,
    branch_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get branch details
    """
    import uuid
    
    # Convert IDs to UUID
    try:
        company_uuid = uuid.UUID(company_id)
        branch_uuid = uuid.UUID(branch_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid company or branch ID format"
        )
    
    result = await db.execute(
        select(CompanyBranch).where(
            and_(
                CompanyBranch.branch_id == branch_uuid,
                CompanyBranch.company_id == company_uuid,
            )
        )
    )
    branch = result.scalar_one_or_none()
    
    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Branch not found"
        )
    
    return branch


@router.delete("/{company_id}/branches/{branch_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_branch(
    company_id: str,
    branch_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete branch
    """
    import uuid
    
    # Convert IDs to UUID
    try:
        company_uuid = uuid.UUID(company_id)
        branch_uuid = uuid.UUID(branch_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid company or branch ID format"
        )
    
    result = await db.execute(
        select(CompanyBranch).where(
            and_(
                CompanyBranch.branch_id == branch_uuid,
                CompanyBranch.company_id == company_uuid,
            )
        )
    )
    branch = result.scalar_one_or_none()
    
    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Branch not found"
        )
    
    branch.is_deleted = True
    await db.commit()


# ─── Document Request Tickets ──────────────────────────────────────────────

@router.post("/{company_id}/clients/{client_id}/document-request", response_model=DocumentRequestTicketOut, status_code=status.HTTP_201_CREATED)
async def create_document_request_ticket(
    company_id: str,
    client_id: str,
    request: DocumentRequestTicketCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Client raises a document request ticket
    """
    import uuid
    from app.models.company_v2 import DocumentRequestTicket
    
    # Convert IDs to UUID
    try:
        company_uuid = uuid.UUID(company_id)
        client_uuid = uuid.UUID(client_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid company or client ID format"
        )
    
    # Verify client exists and belongs to company
    client_result = await db.execute(
        select(CompanyClient).where(
            and_(
                CompanyClient.client_id == client_uuid,
                CompanyClient.company_id == company_uuid,
            )
        )
    )
    client = client_result.scalar_one_or_none()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # Create ticket
    ticket = DocumentRequestTicket(
        ticket_id=uuid.uuid4(),
        company_id=company_uuid,
        client_id=client_uuid,
        requested_by_user_id=current_user.user_id,
        document_types=request.document_types,
        description=request.description,
        priority=request.priority,
        status="OPEN",
    )
    db.add(ticket)
    await db.commit()
    
    return DocumentRequestTicketOut.from_orm(ticket)


@router.get("/{company_id}/document-requests", response_model=List[DocumentRequestTicketOut])
async def list_document_request_tickets(
    company_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    status_filter: Optional[str] = Query(None),
):
    """
    List document request tickets for a company (for owner/employees)
    """
    import uuid
    from app.models.company_v2 import DocumentRequestTicket
    
    # Convert company_id to UUID
    try:
        company_uuid = uuid.UUID(company_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid company ID format"
        )
    
    # Verify user has access to company
    company_user_result = await db.execute(
        select(CompanyUser).where(
            and_(
                CompanyUser.user_id == current_user.user_id,
                CompanyUser.company_id == company_uuid,
            )
        )
    )
    if not company_user_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this company"
        )
    
    # Build query
    query = select(DocumentRequestTicket).where(
        DocumentRequestTicket.company_id == company_uuid
    )
    
    if status_filter:
        query = query.where(DocumentRequestTicket.status == status_filter)
    
    result = await db.execute(query.order_by(DocumentRequestTicket.created_at.desc()))
    tickets = result.scalars().all()
    
    return [DocumentRequestTicketOut.from_orm(ticket) for ticket in tickets]


@router.patch("/{company_id}/document-requests/{ticket_id}", response_model=DocumentRequestTicketOut)
async def update_document_request_ticket(
    company_id: str,
    ticket_id: str,
    request: DocumentRequestTicketUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update document request ticket (owner/employee only)
    """
    import uuid
    from app.models.company_v2 import DocumentRequestTicket
    from datetime import datetime, timezone
    
    # Convert IDs to UUID
    try:
        company_uuid = uuid.UUID(company_id)
        ticket_uuid = uuid.UUID(ticket_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid company or ticket ID format"
        )
    
    # Verify user has access to company
    company_user_result = await db.execute(
        select(CompanyUser).where(
            and_(
                CompanyUser.user_id == current_user.user_id,
                CompanyUser.company_id == company_uuid,
            )
        )
    )
    if not company_user_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this company"
        )
    
    # Get ticket
    ticket_result = await db.execute(
        select(DocumentRequestTicket).where(
            and_(
                DocumentRequestTicket.ticket_id == ticket_uuid,
                DocumentRequestTicket.company_id == company_uuid,
            )
        )
    )
    ticket = ticket_result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Update fields
    if request.status:
        ticket.status = request.status
        if request.status == "COMPLETED":
            ticket.completed_at = datetime.now(timezone.utc)
            ticket.completed_by_user_id = current_user.user_id
    
    if request.assigned_to_user_id:
        ticket.assigned_to_user_id = request.assigned_to_user_id
    
    if request.completion_notes:
        ticket.completion_notes = request.completion_notes
    
    await db.commit()
    
    return DocumentRequestTicketOut.from_orm(ticket)
