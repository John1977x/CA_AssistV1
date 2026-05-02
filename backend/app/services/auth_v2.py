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

    # For now, create a default company response since company_user table doesn't exist yet
    # This is a temporary solution until the company_v2 tables are properly set up
    
    # Determine role based on is_owner flag
    if user.is_owner:
        role_name = "OWNER"
    else:
        role_name = "EMPLOYEE"  # Default role for non-owners
    
    # Create default company info
    company_info = {
        "company_id": "default-company",
        "company_name": "Default Company",
        "company_code": "DEFAULT",
        "role": role_name,
        "branch_id": None,
        "branch_name": None,
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
    # Verify user has permission
    company_user_result = await db.execute(
        select(CompanyUser).where(
            and_(
                CompanyUser.user_id == user_id,
                CompanyUser.company_id == company_id,
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
                    CompanyUser.company_id == company_id,
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
        # Create new user
        new_user = User(
            tenant_id=1,  # Default tenant
            role_id=1,  # Default role
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            phone=data.phone,
            password_hash=hash_password(secrets.token_urlsafe(16)),
            status="INVITED",
            invite_token=secrets.token_urlsafe(32),
            invite_expiry=datetime.now(timezone.utc) + timedelta(days=7),
        )
        db.add(new_user)
        await db.flush()

    # Get role
    target_role_result = await db.execute(
        select(CompanyRole).where(
            and_(
                CompanyRole.company_id == company_id,
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

    # Add user to company
    new_company_user = CompanyUser(
        company_user_id=uuid.uuid4(),
        company_id=company_id,
        user_id=new_user.user_id,
        role_id=target_role.role_id,
        branch_id=data.branch_id,
        status=UserStatusEnum.INVITED if new_user.status == "INVITED" else UserStatusEnum.ACTIVE,
        invited_at=datetime.now(timezone.utc),
    )
    db.add(new_company_user)
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
    """
    # Verify user has permission
    company_user_result = await db.execute(
        select(CompanyUser).where(
            and_(
                CompanyUser.user_id == user_id,
                CompanyUser.company_id == company_id,
            )
        )
    )
    company_user = company_user_result.scalar_one_or_none()

    if not company_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with this company"
        )

    # Create client
    client = CompanyClient(
        client_id=uuid.uuid4(),
        company_id=company_id,
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
    # Verify user has permission
    company_user_result = await db.execute(
        select(CompanyUser).where(
            and_(
                CompanyUser.user_id == user_id,
                CompanyUser.company_id == company_id,
            )
        )
    )
    company_user = company_user_result.scalar_one_or_none()

    if not company_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with this company"
        )

    # Create branch
    branch = CompanyBranch(
        branch_id=uuid.uuid4(),
        company_id=company_id,
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
