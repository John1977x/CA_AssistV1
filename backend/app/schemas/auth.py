from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from typing import Optional, Any, Dict, List
from datetime import datetime, date
import re


# ─── Token Schemas ───────────────────────────────────────────────────────────

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserOut"


class TokenRefresh(BaseModel):
    refresh_token: str


class TokenData(BaseModel):
    user_id: Optional[int] = None
    tenant_id: Optional[int] = None


# ─── Login / Register ────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    totp_code: Optional[str] = None
    remember_me: bool = False


class RegisterTenantRequest(BaseModel):
    # Firm details
    firm_name: str = Field(..., min_length=2, max_length=200)
    owner_name: str = Field(..., min_length=2, max_length=150)
    tenant_code: str = Field(..., min_length=3, max_length=30, pattern=r'^[a-z0-9-]+$')
    membership_number: Optional[str] = None

    # Contact
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=15)
    password: str = Field(..., min_length=8)
    confirm_password: str

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if not re.match(r'^[6-9]\d{9}$', v.replace("+91", "").replace(" ", "")):
            raise ValueError("Enter a valid Indian mobile number")
        return v


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str

    @model_validator(mode="after")
    def passwords_match(self):
        if self.new_password != self.confirm_password:
            raise ValueError("New passwords do not match")
        return self


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str

    @model_validator(mode="after")
    def passwords_match(self):
        if self.new_password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


# ─── User Schemas ────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = None
    role_id: int
    branch_id: Optional[int] = None
    designation: Optional[str] = None
    membership_number: Optional[str] = None
    is_owner: Optional[bool] = False


class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = None
    role_id: Optional[int] = None
    branch_id: Optional[int] = None
    designation: Optional[str] = None
    membership_number: Optional[str] = None
    status: Optional[str] = None
    avatar_url: Optional[str] = None


class UserOut(BaseModel):
    user_id: int
    tenant_id: int
    role_id: int
    branch_id: Optional[int]
    first_name: str
    last_name: str
    display_name: Optional[str]
    email: str
    phone: Optional[str]
    avatar_url: Optional[str]
    designation: Optional[str]
    membership_number: Optional[str]
    is_owner: bool
    is_two_factor_enabled: bool
    status: str
    last_login_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class UserListOut(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    display_name: Optional[str]
    email: str
    phone: Optional[str]
    avatar_url: Optional[str]
    designation: Optional[str]
    is_owner: bool
    status: str
    last_login_at: Optional[datetime]
    role_id: int
    branch_id: Optional[int]
    # Relationships removed to avoid greenlet errors
    # role: Optional["RoleOut"] = None
    # branch: Optional["BranchOut"] = None

    model_config = {"from_attributes": True}


# ─── Role Schemas ────────────────────────────────────────────────────────────

class RoleCreate(BaseModel):
    role_name: str = Field(..., min_length=2, max_length=100)
    role_code: str = Field(..., min_length=2, max_length=30, pattern=r'^[A-Z_]+$')
    description: Optional[str] = None
    permissions_json: Dict[str, Any] = {}
    can_manage_users: bool = False
    can_view_billing: bool = False
    can_approve_task: bool = False


class RoleUpdate(BaseModel):
    role_name: Optional[str] = None
    description: Optional[str] = None
    permissions_json: Optional[Dict[str, Any]] = None
    can_manage_users: Optional[bool] = None
    can_view_billing: Optional[bool] = None
    can_approve_task: Optional[bool] = None
    is_active: Optional[bool] = None


class RoleOut(BaseModel):
    role_id: int
    role_name: str
    role_code: str
    description: Optional[str]
    permissions_json: Dict[str, Any]
    is_system_role: bool
    can_manage_users: bool
    can_view_billing: bool
    can_approve_task: bool
    is_active: bool

    model_config = {"from_attributes": True}


# ─── Branch Schemas ──────────────────────────────────────────────────────────

class BranchCreate(BaseModel):
    branch_name: str = Field(..., min_length=2, max_length=150)
    branch_code: str = Field(..., min_length=2, max_length=20, pattern=r'^[A-Z0-9-]+$')
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    gstin: Optional[str] = None
    manager_user_id: Optional[int] = None
    is_head_office: bool = False


class BranchUpdate(BaseModel):
    branch_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    gstin: Optional[str] = None
    manager_user_id: Optional[int] = None
    is_head_office: Optional[bool] = None
    is_active: Optional[bool] = None


class BranchOut(BaseModel):
    branch_id: int
    branch_name: str
    branch_code: str
    email: Optional[str]
    phone: Optional[str]
    city: Optional[str]
    state: Optional[str]
    is_head_office: bool
    is_active: bool

    model_config = {"from_attributes": True}


# ─── Tenant Schemas ──────────────────────────────────────────────────────────

class TenantOut(BaseModel):
    tenant_id: int
    tenant_code: str
    firm_name: str
    owner_name: str
    email: str
    phone: str
    membership_number: Optional[str]
    gstin: Optional[str]
    pan: Optional[str]
    address_line1: Optional[str]
    city: Optional[str]
    state: Optional[str]
    pincode: Optional[str]
    country: str
    logo_url: Optional[str]
    timezone: str
    currency_code: str
    status: str
    trial_end_date: Optional[date]
    created_at: datetime

    model_config = {"from_attributes": True}


class TenantUpdate(BaseModel):
    firm_name: Optional[str] = None
    owner_name: Optional[str] = None
    phone: Optional[str] = None
    alternate_phone: Optional[str] = None
    membership_number: Optional[str] = None
    gstin: Optional[str] = None
    pan: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    logo_url: Optional[str] = None
    timezone: Optional[str] = None


# ─── 2FA Schemas ─────────────────────────────────────────────────────────────

class Enable2FAResponse(BaseModel):
    qr_code: str      # base64 PNG
    secret: str       # backup key


class Verify2FARequest(BaseModel):
    totp_code: str = Field(..., min_length=6, max_length=6)


# ─── Pagination ──────────────────────────────────────────────────────────────

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int


# ─── Generic ─────────────────────────────────────────────────────────────────

class MessageResponse(BaseModel):
    message: str
    success: bool = True
