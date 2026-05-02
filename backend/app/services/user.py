from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, and_, or_
from fastapi import HTTPException
from datetime import datetime, timezone, timedelta
from typing import Optional, List

from app.models.auth import User, UserRole, Branch
from app.schemas.auth import UserCreate, UserUpdate, RoleCreate, RoleUpdate, BranchCreate, BranchUpdate
from app.core.security import hash_password, create_invite_token, validate_password_strength
from app.core.config import settings
from app.services.email import send_invite_email


# ─── User Management ─────────────────────────────────────────────────────────

async def get_users(
    db: AsyncSession,
    tenant_id: int,
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None,
    status: Optional[str] = None,
    role_id: Optional[int] = None,
    branch_id: Optional[int] = None,
):
    query = select(User).where(User.tenant_id == tenant_id, User.is_deleted == False)

    if search:
        query = query.where(
            or_(
                User.first_name.ilike(f"%{search}%"),
                User.last_name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.display_name.ilike(f"%{search}%"),
            )
        )
    if status:
        query = query.where(User.status == status)
    if role_id:
        query = query.where(User.role_id == role_id)
    if branch_id:
        query = query.where(User.branch_id == branch_id)

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()

    query = query.offset((page - 1) * page_size).limit(page_size).order_by(User.created_at.desc())
    result = await db.execute(query)
    users = result.scalars().all()

    return users, total


async def get_user_by_id(db: AsyncSession, tenant_id: int, user_id: int) -> User:
    result = await db.execute(
        select(User).where(
            User.user_id == user_id,
            User.tenant_id == tenant_id,
            User.is_deleted == False,
        )
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user


async def invite_user(db: AsyncSession, tenant_id: int, data: UserCreate, invited_by: User) -> User:
    # Check max users limit
    result = await db.execute(
        select(func.count(User.user_id)).where(
            User.tenant_id == tenant_id,
            User.is_deleted == False,
            User.status.in_(["ACTIVE", "INVITED"]),
        )
    )
    user_count = result.scalar()

    from app.models.auth import Tenant
    tenant_result = await db.execute(
        select(Tenant).where(Tenant.tenant_id == tenant_id)
    )
    tenant = tenant_result.scalar_one_or_none()
    sub = tenant.subscription if tenant else None
    if sub and sub.max_users and user_count >= sub.max_users:
        raise HTTPException(
            status_code=400,
            detail=f"User limit reached ({sub.max_users}). Upgrade your plan to add more users.",
        )

    # Check email not already in this tenant
    existing = await db.execute(
        select(User).where(User.tenant_id == tenant_id, User.email == data.email, User.is_deleted == False)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="A user with this email already exists in your firm.")

    # Validate role belongs to tenant
    role_result = await db.execute(
        select(UserRole).where(
            UserRole.role_id == data.role_id,
            or_(UserRole.tenant_id == tenant_id, UserRole.tenant_id == None),
            UserRole.is_active == True,
        )
    )
    if not role_result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Invalid or inactive role.")

    token = create_invite_token()
    expiry = datetime.now(timezone.utc) + timedelta(hours=settings.INVITE_TOKEN_EXPIRE_HOURS)

    # Extract is_owner from data if present
    is_owner = getattr(data, 'is_owner', False) or False

    user = User(
        tenant_id=tenant_id,
        role_id=data.role_id,
        branch_id=data.branch_id,
        first_name=data.first_name,
        last_name=data.last_name,
        display_name=f"{data.first_name} {data.last_name}",
        email=data.email,
        phone=data.phone,
        designation=data.designation,
        membership_number=data.membership_number,
        is_owner=is_owner,
        password_hash=hash_password(secrets.token_urlsafe(16)),  # Placeholder
        status="INVITED",
        invite_token=token,
        invite_expiry=expiry,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    try:
        await send_invite_email(
            to_email=data.email,
            to_name=f"{data.first_name} {data.last_name}",
            firm_name=invited_by.tenant.firm_name if invited_by.tenant else "",
            token=token,
        )
    except Exception:
        pass

    return user


import secrets


async def accept_invite(db: AsyncSession, token: str, password: str) -> User:
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(User).where(
            User.invite_token == token,
            User.invite_expiry > now,
            User.status == "INVITED",
        )
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired invite link.")

    valid, msg = validate_password_strength(password)
    if not valid:
        raise HTTPException(status_code=400, detail=msg)

    await db.execute(
        update(User)
        .where(User.user_id == user.user_id)
        .values(
            password_hash=hash_password(password),
            status="ACTIVE",
            invite_token=None,
            invite_expiry=None,
            password_changed_at=now,
        )
    )
    await db.commit()
    await db.refresh(user)
    return user


async def update_user(db: AsyncSession, tenant_id: int, user_id: int, data: UserUpdate) -> User:
    user = await get_user_by_id(db, tenant_id, user_id)
    update_data = data.model_dump(exclude_unset=True)

    if "role_id" in update_data:
        role_result = await db.execute(
            select(UserRole).where(
                UserRole.role_id == update_data["role_id"],
                or_(UserRole.tenant_id == tenant_id, UserRole.tenant_id == None),
            )
        )
        if not role_result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Invalid role.")

    if update_data:
        if "first_name" in update_data or "last_name" in update_data:
            fn = update_data.get("first_name", user.first_name)
            ln = update_data.get("last_name", user.last_name)
            update_data["display_name"] = f"{fn} {ln}"
        await db.execute(update(User).where(User.user_id == user_id).values(**update_data))
        await db.commit()
        await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, tenant_id: int, user_id: int, current_user: User):
    user = await get_user_by_id(db, tenant_id, user_id)
    if user.is_owner:
        raise HTTPException(status_code=400, detail="Cannot delete the firm owner.")
    if user.user_id == current_user.user_id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account.")
    await db.execute(
        update(User)
        .where(User.user_id == user_id)
        .values(is_deleted=True, status="INACTIVE")
    )
    await db.commit()


# ─── Role Management ─────────────────────────────────────────────────────────

async def get_roles(db: AsyncSession, tenant_id: int) -> List[UserRole]:
    result = await db.execute(
        select(UserRole).where(
            or_(UserRole.tenant_id == tenant_id, UserRole.tenant_id == None),
            UserRole.is_active == True,
        ).order_by(UserRole.sort_order)
    )
    return result.scalars().all()


async def create_role(db: AsyncSession, tenant_id: int, data: RoleCreate) -> UserRole:
    # Check code uniqueness within tenant
    existing = await db.execute(
        select(UserRole).where(UserRole.tenant_id == tenant_id, UserRole.role_code == data.role_code)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Role code already exists.")

    role = UserRole(
        tenant_id=tenant_id,
        **data.model_dump(),
    )
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role


async def update_role(db: AsyncSession, tenant_id: int, role_id: int, data: RoleUpdate) -> UserRole:
    result = await db.execute(
        select(UserRole).where(UserRole.role_id == role_id, UserRole.tenant_id == tenant_id)
    )
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found.")
    if role.is_system_role:
        raise HTTPException(status_code=400, detail="Cannot modify system roles.")

    update_data = data.model_dump(exclude_unset=True)
    if update_data:
        await db.execute(update(UserRole).where(UserRole.role_id == role_id).values(**update_data))
        await db.commit()
        await db.refresh(role)
    return role


async def delete_role(db: AsyncSession, tenant_id: int, role_id: int):
    result = await db.execute(
        select(UserRole).where(UserRole.role_id == role_id, UserRole.tenant_id == tenant_id)
    )
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found.")
    if role.is_system_role:
        raise HTTPException(status_code=400, detail="Cannot delete system roles.")

    # Check if any users have this role
    users_check = await db.execute(
        select(func.count(User.user_id)).where(User.role_id == role_id, User.is_deleted == False)
    )
    if users_check.scalar() > 0:
        raise HTTPException(status_code=400, detail="Cannot delete role assigned to users.")

    await db.execute(update(UserRole).where(UserRole.role_id == role_id).values(is_active=False))
    await db.commit()


# ─── Branch Management ───────────────────────────────────────────────────────

async def get_branches(db: AsyncSession, tenant_id: int) -> List[Branch]:
    result = await db.execute(
        select(Branch).where(Branch.tenant_id == tenant_id, Branch.is_active == True)
        .order_by(Branch.is_head_office.desc(), Branch.branch_name)
    )
    return result.scalars().all()


async def create_branch(db: AsyncSession, tenant_id: int, data: BranchCreate) -> Branch:
    existing = await db.execute(
        select(Branch).where(Branch.tenant_id == tenant_id, Branch.branch_code == data.branch_code)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Branch code already exists.")

    if data.is_head_office:
        # Unset existing head office
        await db.execute(
            update(Branch).where(Branch.tenant_id == tenant_id).values(is_head_office=False)
        )

    branch = Branch(tenant_id=tenant_id, **data.model_dump())
    db.add(branch)
    await db.commit()
    await db.refresh(branch)
    return branch


async def update_branch(db: AsyncSession, tenant_id: int, branch_id: int, data: BranchUpdate) -> Branch:
    result = await db.execute(
        select(Branch).where(Branch.branch_id == branch_id, Branch.tenant_id == tenant_id)
    )
    branch = result.scalar_one_or_none()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found.")

    update_data = data.model_dump(exclude_unset=True)
    if update_data.get("is_head_office"):
        await db.execute(
            update(Branch).where(Branch.tenant_id == tenant_id).values(is_head_office=False)
        )
    if update_data:
        await db.execute(update(Branch).where(Branch.branch_id == branch_id).values(**update_data))
        await db.commit()
        await db.refresh(branch)
    return branch
