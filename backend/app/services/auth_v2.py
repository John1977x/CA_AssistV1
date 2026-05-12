"""
New Authentication Service for Multi-Company, Multi-Role Architecture
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from fastapi import HTTPException, status
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple
import secrets
import uuid

from app.models.auth import User, Tenant, Subscription, UserRole
from app.models.company_v2 import (
    Company, CompanyBranch, CompanyRole, CompanyUser, CompanyClient,
    CompanyRoleEnum, UserStatusEnum
)
from app.schemas.auth_v2 import (
    OwnerRegisterRequest, OwnerRegisterResponse,
    LoginRequest, LoginResponse, UserProfile, CompanyInfo,
    CreateCompanyRequest, CompanyOut,
    AddTeamMemberRequest, TeamMemberOut,
    AddClientRequest, ClientOut,
    CreateBranchRequest, BranchOut,
)
from app.core.security import (
    hash_password, verify_password, validate_password_strength,
    create_access_token, create_refresh_token, decode_token,
)
from app.core.config import settings


# ─── Owner Registration ──────────────────────────────────────────────────────

async def register_owner(db: AsyncSession, data: OwnerRegisterRequest) -> OwnerRegisterResponse:
    """
    Register a new owner and create their first company
    """
    # Check email uniqueness
    existing_user = await db.execute(
        select(User).where(User.email == data.email)
    )
    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check company code uniqueness
    existing_company = await db.execute(
        select(Company).where(Company.company_code == data.company_code)
    )
    if existing_company.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company code already taken"
        )

    # Validate password
    valid, msg = validate_password_strength(data.password)
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=msg
        )

    # Get or create default trial subscription
    sub_result = await db.execute(
        select(Subscription).where(
            and_(
                Subscription.plan_code == "TRIAL",
                Subscription.is_active == True
            )
        )
    )
    subscription = sub_result.scalar_one_or_none()
    if not subscription:
        subscription = Subscription(
            plan_name="Trial",
            plan_code="TRIAL",
            price_monthly=0,
            max_users=10,
            max_clients=50,
            max_branches=5,
            trial_days=14,
            features_json={"gst": True, "itr": True, "tds": False, "audit": False},
        )
        db.add(subscription)
        await db.flush()

    # Create tenant (for system-level management)
    tenant = Tenant(
        subscription_id=subscription.subscription_id,
        tenant_code=f"TENANT_{secrets.token_hex(4).upper()}",
        firm_name=data.company_name,
        owner_name=f"{data.first_name} {data.last_name}",
        email=data.email,
        phone=data.phone,
        status="ACTIVE",
        trial_end_date=datetime.now(timezone.utc).date() + timedelta(days=subscription.trial_days),
    )
    db.add(tenant)
    await db.flush()

    # Get or create default role for this tenant
    role_result = await db.execute(
        select(UserRole).where(
            and_(
                UserRole.tenant_id == tenant.tenant_id,
                UserRole.role_code == "OWNER"
            )
        )
    )
    default_role = role_result.scalar_one_or_none()
    
    if not default_role:
        default_role = UserRole(
            tenant_id=tenant.tenant_id,
            role_name="Owner",
            role_code="OWNER",
            description="Tenant Owner",
            is_system_role=False,
            can_manage_users=True,
            can_view_billing=True,
            can_approve_task=True,
            is_active=True,
        )
        db.add(default_role)
        await db.flush()

    # Create user (owner)
    user = User(
        tenant_id=tenant.tenant_id,
        role_id=default_role.role_id,
        first_name=data.first_name,
        last_name=data.last_name,
        display_name=f"{data.first_name} {data.last_name}",
        email=data.email,
        phone=data.phone,
        password_hash=hash_password(data.password),
        is_owner=True,
        status="ACTIVE",
    )
    db.add(user)
    await db.flush()

    # Create company
    company = Company(
        company_id=uuid.uuid4(),
        owner_id=user.user_id,
        company_name=data.company_name,
        company_code=data.company_code,
        email=data.email,
        phone=data.phone,
        status="ACTIVE",
    )
    db.add(company)
    await db.flush()

    # Create default company roles
    owner_role = CompanyRole(
        role_id=uuid.uuid4(),
        company_id=company.company_id,
        role_name=CompanyRoleEnum.OWNER,
        description="Company Owner",
        permissions={"all": True},
    )
    manager_role = CompanyRole(
        role_id=uuid.uuid4(),
        company_id=company.company_id,
        role_name=CompanyRoleEnum.MANAGER,
        description="Company Manager",
        permissions={"team": True, "clients": True, "tasks": True},
    )
    employee_role = CompanyRole(
        role_id=uuid.uuid4(),
        company_id=company.company_id,
        role_name=CompanyRoleEnum.EMPLOYEE,
        description="Company Employee",
        permissions={"tasks": True, "team": True},
    )
    client_role = CompanyRole(
        role_id=uuid.uuid4(),
        company_id=company.company_id,
        role_name=CompanyRoleEnum.CLIENT,
        description="Company Client",
        permissions={"tasks": True},
    )
    db.add_all([owner_role, manager_role, employee_role, client_role])
    await db.flush()

    # Add owner to company
    company_user = CompanyUser(
        company_user_id=uuid.uuid4(),
        company_id=company.company_id,
        user_id=user.user_id,
        role_id=owner_role.role_id,
        status=UserStatusEnum.ACTIVE,
        joined_at=datetime.now(timezone.utc),
    )
    db.add(company_user)

    # Create head office branch
    head_branch = CompanyBranch(
        branch_id=uuid.uuid4(),
        company_id=company.company_id,
        branch_name="Head Office",
        branch_code="HO",
        email=data.email,
        phone=data.phone,
        is_head_office=True,
        status="ACTIVE",
    )
    db.add(head_branch)

    await db.commit()

    return OwnerRegisterResponse(
        user_id=user.user_id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        company_id=str(company.company_id),
        company_name=company.company_name,
        message="Owner registered successfully. Please login to continue.",
    )


# ─── Login ───────────────────────────────────────────────────────────────────

async def login_user(db: AsyncSession, data: LoginRequest) -> LoginResponse:
    """
    Login user and return tokens with company info
    """
    # Find user by email
    user_result = await db.execute(
        select(User).where(User.email == data.email)
    )
    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Check if user is active
    if user.status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is not active"
        )

    # Check if user is locked
    if user.locked_until and user.locked_until > datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is locked. Try again later."
        )

    # Verify password
    if not verify_password(data.password, user.password_hash):
        # Increment failed login attempts
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= 5:
            user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=30)
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Reset failed login attempts
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login_at = datetime.now(timezone.utc)

    # Check if user is a client first by checking their role
    role_result = await db.execute(
        select(UserRole).where(UserRole.role_id == user.role_id)
    )
    user_role = role_result.scalar_one_or_none()
    is_client = user_role and user_role.role_name == "CLIENT"
    
    # Get company and branch info for the user (get most recent if multiple)
    company_user_result = await db.execute(
        select(CompanyUser).where(CompanyUser.user_id == user.user_id).order_by(CompanyUser.created_at.desc()).limit(1)
    )
    company_user = company_user_result.scalar_one_or_none()
    
    # Check if user is a client via CompanyClient (legacy support)
    client_result = await db.execute(
        select(CompanyClient).where(CompanyClient.user_id == user.user_id).limit(1)
    )
    company_client = client_result.scalar_one_or_none()
    
    # Default company info (fallback if user has no company assignment)
    company_info = {
        "company_id": None,
        "company_name": None,
        "company_code": None,
        "role": "OWNER" if user.is_owner else ("CLIENT" if (is_client or company_client) else "EMPLOYEE"),
        "branch_id": None,
        "branch_name": None,
        "client_id": None,
    }
    
    # If user is a client (via role), get client's company info
    if is_client:
        # For customers created as clients, they don't have a company yet
        # Just return CLIENT role
        company_info = {
            "company_id": None,
            "company_name": None,
            "company_code": None,
            "role": "CLIENT",
            "branch_id": None,
            "branch_name": None,
            "client_id": None,
        }
    # If user is a client via CompanyClient (legacy)
    elif company_client:
        client_company_result = await db.execute(
            select(Company).where(Company.company_id == company_client.company_id)
        )
        client_company = client_company_result.scalar_one_or_none()
        
        if client_company:
            company_info = {
                "company_id": str(client_company.company_id),
                "company_name": client_company.company_name,
                "company_code": client_company.company_code,
                "role": "CLIENT",
                "branch_id": None,
                "branch_name": None,
                "client_id": str(company_client.client_id),
            }
    elif company_user:
        # Get company details
        company_result = await db.execute(
            select(Company).where(Company.company_id == company_user.company_id)
        )
        company = company_result.scalar_one_or_none()
        
        # Get role details
        role_result = await db.execute(
            select(CompanyRole).where(CompanyRole.role_id == company_user.role_id)
        )
        role = role_result.scalar_one_or_none()
        
        # Get branch details if assigned
        branch_info = None
        if company_user.branch_id:
            branch_result = await db.execute(
                select(CompanyBranch).where(CompanyBranch.branch_id == company_user.branch_id)
            )
            branch_info = branch_result.scalar_one_or_none()
        
        if company:
            company_info = {
                "company_id": str(company.company_id),
                "company_name": company.company_name,
                "company_code": company.company_code,
                "role": role.role_name if role else ("OWNER" if user.is_owner else "EMPLOYEE"),
                "branch_id": str(company_user.branch_id) if company_user.branch_id else None,
                "branch_name": branch_info.branch_name if branch_info else None,
                "client_id": None,
            }
    elif user.is_owner:
        # For owners with no company assignment, get their first owned company
        owner_company_result = await db.execute(
            select(Company).where(Company.owner_id == user.user_id).limit(1)
        )
        owner_company = owner_company_result.scalar_one_or_none()
        
        if owner_company:
            company_info = {
                "company_id": str(owner_company.company_id),
                "company_name": owner_company.company_name,
                "company_code": owner_company.company_code,
                "role": "OWNER",
                "branch_id": None,
                "branch_name": None,
                "client_id": None,
            }

    # Create tokens
    access_token = create_access_token(
        subject=user.user_id,
        extra={
            "email": user.email,
            "company_id": company_info["company_id"],
            "role": company_info["role"],
        }
    )
    refresh_token = create_refresh_token(
        subject=user.user_id
    )

    await db.commit()

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserProfile(
            user_id=user.user_id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            display_name=user.display_name,
            phone=user.phone,
            avatar_url=user.avatar_url,
            is_owner=user.is_owner,
            is_two_factor_enabled=user.is_two_factor_enabled,
            status=user.status,
        ),
        company=CompanyInfo(
            company_id=company_info["company_id"],
            company_name=company_info["company_name"],
            company_code=company_info["company_code"],
            role=company_info["role"],
            branch_id=company_info.get("branch_id"),
            branch_name=company_info.get("branch_name"),
            client_id=company_info.get("client_id"),
        ),
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


# ─── Company Management ──────────────────────────────────────────────────────

async def create_company(
    db: AsyncSession,
    user_id: int,
    data: CreateCompanyRequest
) -> CompanyOut:
    """
    Create a new company (owner only)
    """
    # Get user
    user_result = await db.execute(
        select(User).where(User.user_id == user_id)
    )
    user = user_result.scalar_one_or_none()

    if not user or not user.is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners can create companies"
        )

    # Check company code uniqueness
    existing = await db.execute(
        select(Company).where(Company.company_code == data.company_code)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company code already taken"
        )

    # Create company
    company = Company(
        company_id=uuid.uuid4(),
        owner_id=user_id,
        company_name=data.company_name,
        company_code=data.company_code,
        email=data.email,
        phone=data.phone,
        address_line1=data.address_line1,
        address_line2=data.address_line2,
        city=data.city,
        state=data.state,
        pincode=data.pincode,
        pan=data.pan,
        gstin=data.gstin,
        cin=data.cin,
        status="ACTIVE",
    )
    db.add(company)
    await db.flush()

    # Create default roles
    for role_name in [CompanyRoleEnum.OWNER, CompanyRoleEnum.MANAGER, CompanyRoleEnum.EMPLOYEE, CompanyRoleEnum.CLIENT]:
        role = CompanyRole(
            role_id=uuid.uuid4(),
            company_id=company.company_id,
            role_name=role_name,
            permissions={},
        )
        db.add(role)

    await db.commit()

    return CompanyOut.from_orm(company)


# ─── Team Management ────────────────────────────────────────────────────────

async def add_team_member(
    db: AsyncSession,
    user_id: int,
    company_id: str,
    data: AddTeamMemberRequest
) -> TeamMemberOut:
    """
    Add a team member to a company (owner/manager only)
    """
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
                CompanyUser.user_id == user_id,
                CompanyUser.company_id == company_uuid,
            )
        )
    )
    company_user = company_user_result.scalar_one_or_none()

    if not company_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with this company"
        )

    # Check if user has permission to add team members
    role_result = await db.execute(
        select(CompanyRole).where(CompanyRole.role_id == company_user.role_id)
    )
    role = role_result.scalar_one_or_none()

    if role.role_name not in [CompanyRoleEnum.OWNER, CompanyRoleEnum.MANAGER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to add team members"
        )

    # Check if user already exists
    existing_user = await db.execute(
        select(User).where(User.email == data.email)
    )
    existing = existing_user.scalar_one_or_none()

    if existing:
        # Check if already in company
        existing_company_user = await db.execute(
            select(CompanyUser).where(
                and_(
                    CompanyUser.user_id == existing.user_id,
                    CompanyUser.company_id == company_uuid,
                )
            )
        )
        if existing_company_user.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already in this company"
            )
        new_user = existing
    else:
        # Create new user with default password
        # Get the company owner to get the correct tenant_id
        company_result = await db.execute(
            select(Company).where(Company.company_id == company_uuid)
        )
        company = company_result.scalar_one_or_none()
        
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        # Get a valid role for the tenant (use EMPLOYEE role or first available)
        role_result = await db.execute(
            select(UserRole).where(
                UserRole.tenant_id == company.owner.tenant_id
            ).limit(1)
        )
        valid_role = role_result.scalar_one_or_none()
        
        if not valid_role:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No roles available for this tenant"
            )
        
        default_password = "CAassists@123456"
        new_user = User(
            tenant_id=company.owner.tenant_id,  # Use company owner's tenant
            role_id=valid_role.role_id,  # Use valid role from tenant
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            phone=data.phone,
            password_hash=hash_password(default_password),
            status="ACTIVE",
        )
        db.add(new_user)
        await db.flush()

    # Get role
    target_role_result = await db.execute(
        select(CompanyRole).where(
            and_(
                CompanyRole.company_id == company_uuid,
                CompanyRole.role_name == data.role,
            )
        )
    )
    target_role = target_role_result.scalar_one_or_none()

    if not target_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role"
        )

    # Convert branch_id to UUID if provided
    branch_uuid = None
    if data.branch_id:
        try:
            branch_uuid = uuid.UUID(data.branch_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid branch ID format"
            )

    # Add user to company
    new_company_user = CompanyUser(
        company_user_id=uuid.uuid4(),
        company_id=company_uuid,
        user_id=new_user.user_id,
        role_id=target_role.role_id,
        branch_id=branch_uuid,
        status=UserStatusEnum.INVITED if new_user.status == "INVITED" else UserStatusEnum.ACTIVE,
        invited_at=datetime.now(timezone.utc),
    )
    db.add(new_company_user)
    await db.flush()
    
    # Refresh to get relationships loaded
    await db.refresh(new_company_user, ['user', 'role'])
    await db.commit()

    return TeamMemberOut.from_orm(new_company_user)


# ─── Client Management ──────────────────────────────────────────────────────

async def add_client(
    db: AsyncSession,
    user_id: int,
    company_id: str,
    data: AddClientRequest
) -> ClientOut:
    """
    Add a client to a company (owner/manager only)
    Creates a User account with default password if email is provided
    """
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
                CompanyUser.user_id == user_id,
                CompanyUser.company_id == company_uuid,
            )
        )
    )
    company_user = company_user_result.scalar_one_or_none()

    if not company_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with this company"
        )

    # If email is provided, create a User account for the client
    client_user_id = None
    if data.email:
        # Check if user already exists
        existing_user_result = await db.execute(
            select(User).where(User.email == data.email)
        )
        existing_user = existing_user_result.scalar_one_or_none()
        
        if existing_user:
            client_user_id = existing_user.user_id
        else:
            # Get company to resolve tenant_id
            company_result = await db.execute(
                select(Company).where(Company.company_id == company_uuid)
            )
            company = company_result.scalar_one_or_none()
            if not company:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

            # Look up CLIENT role for this tenant, fall back to any available role
            client_role_result = await db.execute(
                select(UserRole).where(
                    UserRole.tenant_id == company.owner.tenant_id,
                    UserRole.role_code == "CLIENT",
                ).limit(1)
            )
            client_role = client_role_result.scalar_one_or_none()
            if not client_role:
                fallback_result = await db.execute(
                    select(UserRole).where(UserRole.tenant_id == company.owner.tenant_id).limit(1)
                )
                client_role = fallback_result.scalar_one_or_none()
            if not client_role:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="No roles available for this tenant",
                )

            # Create new user with default password
            default_password = "CAassists@123456"
            name_parts = (data.client_name or "Client User").split()
            new_user = User(
                tenant_id=company.owner.tenant_id,
                role_id=client_role.role_id,
                email=data.email,
                first_name=name_parts[0],
                last_name=name_parts[-1] if len(name_parts) > 1 else "User",
                password_hash=hash_password(default_password),
                phone=data.phone,
                is_owner=False,
                status="ACTIVE",
                is_email_verified=False,
                failed_login_attempts=0,
            )
            db.add(new_user)
            await db.flush()
            client_user_id = new_user.user_id

    # Create client
    client = CompanyClient(
        client_id=uuid.uuid4(),
        company_id=company_uuid,
        user_id=client_user_id,
        client_name=data.client_name,
        client_code=data.client_code,
        email=data.email,
        phone=data.phone,
        pan=data.pan,
        gstin=data.gstin,
        client_type=data.client_type,
        status="ACTIVE",
    )
    db.add(client)
    await db.commit()

    return ClientOut.from_orm(client)


# ─── Branch Management ──────────────────────────────────────────────────────

async def create_branch(
    db: AsyncSession,
    user_id: int,
    company_id: str,
    data: CreateBranchRequest
) -> BranchOut:
    """
    Create a branch for a company (owner/manager only)
    """
    # Convert company_id string to UUID
    try:
        company_uuid = uuid.UUID(company_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid company ID format"
        )
    
    # Verify user has permission (owner or manager)
    company_user_result = await db.execute(
        select(CompanyUser).where(
            and_(
                CompanyUser.user_id == user_id,
                CompanyUser.company_id == company_uuid,
            )
        )
    )
    company_user = company_user_result.scalar_one_or_none()

    if not company_user:
        # Also check if user is the owner
        company_result = await db.execute(
            select(Company).where(Company.company_id == company_uuid)
        )
        company = company_result.scalar_one_or_none()
        if not company or company.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User not associated with this company"
            )

    # Create branch
    branch = CompanyBranch(
        branch_id=uuid.uuid4(),
        company_id=company_uuid,
        branch_name=data.branch_name,
        branch_code=data.branch_code,
        email=data.email,
        phone=data.phone,
        address_line1=data.address_line1,
        address_line2=data.address_line2,
        city=data.city,
        state=data.state,
        pincode=data.pincode,
        is_head_office=data.is_head_office,
        manager_id=data.manager_id,
        status="ACTIVE",
    )
    db.add(branch)
    await db.commit()

    return BranchOut.from_orm(branch)


# ─── Change Company/Branch ──────────────────────────────────────────────────

async def change_company_branch(
    db: AsyncSession,
    user_id: int,
    company_id: str,
    branch_id: Optional[str] = None
) -> CompanyInfo:
    """
    Change user's company and branch (owner only)
    """
    # Convert company_id to UUID
    try:
        company_uuid = uuid.UUID(company_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid company ID format"
        )
    
    # Convert branch_id to UUID if provided
    branch_uuid = None
    if branch_id:
        try:
            branch_uuid = uuid.UUID(branch_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid branch ID format"
            )
    
    # Get user
    user_result = await db.execute(
        select(User).where(User.user_id == user_id)
    )
    user = user_result.scalar_one_or_none()

    if not user or not user.is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners can change company and branch"
        )

    # Verify company exists
    company_result = await db.execute(
        select(Company).where(Company.company_id == company_uuid)
    )
    company = company_result.scalar_one_or_none()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )

    # Verify user is associated with this company (or is the owner)
    company_user_result = await db.execute(
        select(CompanyUser).where(
            and_(
                CompanyUser.user_id == user_id,
                CompanyUser.company_id == company_uuid,
            )
        )
    )
    company_user = company_user_result.scalar_one_or_none()

    # If user is not in CompanyUser table but is the owner, create an entry
    if not company_user:
        if company.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User not associated with this company"
            )
        
        # Create CompanyUser entry for owner
        # Get or create OWNER role for this company
        owner_role_result = await db.execute(
            select(CompanyRole).where(
                and_(
                    CompanyRole.company_id == company_uuid,
                    CompanyRole.role_name == "OWNER",
                )
            )
        )
        owner_role = owner_role_result.scalar_one_or_none()
        
        if not owner_role:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="OWNER role not found for company"
            )
        
        # Create CompanyUser entry
        company_user = CompanyUser(
            company_user_id=uuid.uuid4(),
            company_id=company_uuid,
            user_id=user_id,
            role_id=owner_role.role_id,
            status="ACTIVE",
            joined_at=datetime.now(timezone.utc),
        )
        db.add(company_user)
        await db.flush()

    # Verify branch exists if provided
    branch_info = None
    if branch_uuid:
        branch_result = await db.execute(
            select(CompanyBranch).where(
                and_(
                    CompanyBranch.branch_id == branch_uuid,
                    CompanyBranch.company_id == company_uuid,
                )
            )
        )
        branch_info = branch_result.scalar_one_or_none()

        if not branch_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Branch not found in this company"
            )

    # Update company user's branch
    company_user.branch_id = branch_uuid
    await db.commit()

    # Get role details
    role_result = await db.execute(
        select(CompanyRole).where(CompanyRole.role_id == company_user.role_id)
    )
    role = role_result.scalar_one_or_none()

    return CompanyInfo(
        company_id=str(company.company_id),
        company_name=company.company_name,
        company_code=company.company_code,
        role=role.role_name if role else "OWNER",
        branch_id=str(branch_uuid) if branch_uuid else None,
        branch_name=branch_info.branch_name if branch_info else None,
    )
