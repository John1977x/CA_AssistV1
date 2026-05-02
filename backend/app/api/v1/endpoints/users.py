from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
import math

from app.db.session import get_db
from app.core.deps import get_current_active_user, require_can_manage_users, get_current_tenant
from app.models.auth import User, Tenant
from app.schemas.auth import (
    UserCreate, UserUpdate, UserOut, UserListOut,
    RoleCreate, RoleUpdate, RoleOut,
    BranchCreate, BranchUpdate, BranchOut,
    PaginatedResponse, MessageResponse,
)
from app.services import user as user_svc

router = APIRouter(prefix="/users", tags=["Users"])


# ─── User CRUD ───────────────────────────────────────────────────────────────

@router.get("", response_model=PaginatedResponse)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    role_id: Optional[int] = Query(None),
    branch_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    users, total = await user_svc.get_users(
        db, current_user.tenant_id, page, page_size, search, status, role_id, branch_id
    )
    return PaginatedResponse(
        items=[UserListOut.model_validate(u) for u in users],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size),
    )


@router.post("", response_model=UserOut, status_code=201)
async def invite_user(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_can_manage_users),
):
    user = await user_svc.invite_user(db, current_user.tenant_id, data, current_user)
    return UserOut.model_validate(user)


@router.get("/{user_id}", response_model=UserOut)
async def get_user(
    user_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    user = await user_svc.get_user_by_id(db, current_user.tenant_id, user_id)
    return UserOut.model_validate(user)


@router.patch("/{user_id}", response_model=UserOut)
async def update_user(
    data: UserUpdate,
    user_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_can_manage_users),
):
    # Users can update their own profile without manage-users permission
    user = await user_svc.update_user(db, current_user.tenant_id, user_id, data)
    return UserOut.model_validate(user)


@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_can_manage_users),
):
    await user_svc.delete_user(db, current_user.tenant_id, user_id, current_user)
    return MessageResponse(message="User removed successfully.")


@router.post("/accept-invite", response_model=MessageResponse)
async def accept_invite(
    token: str,
    password: str,
    db: AsyncSession = Depends(get_db),
):
    """Accept an email invitation and set password."""
    await user_svc.accept_invite(db, token, password)
    return MessageResponse(message="Account activated successfully. Please login.")


# ─── Roles ───────────────────────────────────────────────────────────────────

roles_router = APIRouter(prefix="/roles", tags=["Roles"])


@roles_router.get("", response_model=List[RoleOut])
async def list_roles(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    roles = await user_svc.get_roles(db, current_user.tenant_id)
    return [RoleOut.model_validate(r) for r in roles]


@roles_router.post("", response_model=RoleOut, status_code=201)
async def create_role(
    data: RoleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_can_manage_users),
):
    role = await user_svc.create_role(db, current_user.tenant_id, data)
    return RoleOut.model_validate(role)


@roles_router.patch("/{role_id}", response_model=RoleOut)
async def update_role(
    data: RoleUpdate,
    role_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_can_manage_users),
):
    role = await user_svc.update_role(db, current_user.tenant_id, role_id, data)
    return RoleOut.model_validate(role)


@roles_router.delete("/{role_id}", response_model=MessageResponse)
async def delete_role(
    role_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_can_manage_users),
):
    await user_svc.delete_role(db, current_user.tenant_id, role_id)
    return MessageResponse(message="Role deleted.")


# ─── Branches ────────────────────────────────────────────────────────────────

branches_router = APIRouter(prefix="/branches", tags=["Branches"])


@branches_router.get("", response_model=List[BranchOut])
async def list_branches(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    branches = await user_svc.get_branches(db, current_user.tenant_id)
    return [BranchOut.model_validate(b) for b in branches]


@branches_router.post("", response_model=BranchOut, status_code=201)
async def create_branch(
    data: BranchCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_can_manage_users),
):
    branch = await user_svc.create_branch(db, current_user.tenant_id, data)
    return BranchOut.model_validate(branch)


@branches_router.patch("/{branch_id}", response_model=BranchOut)
async def update_branch(
    data: BranchUpdate,
    branch_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_can_manage_users),
):
    branch = await user_svc.update_branch(db, current_user.tenant_id, branch_id, data)
    return BranchOut.model_validate(branch)
