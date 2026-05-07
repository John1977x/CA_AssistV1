"""
New Authentication Schemas for Multi-Company, Multi-Role Architecture
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class CompanyRoleEnum(str, Enum):
    """Company roles"""
    OWNER = "OWNER"
    MANAGER = "MANAGER"
    EMPLOYEE = "EMPLOYEE"
    CLIENT = "CLIENT"


class UserStatusEnum(str, Enum):
    """User status"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    INVITED = "INVITED"
    SUSPENDED = "SUSPENDED"


# ─── Registration ────────────────────────────────────────────────────────────

class OwnerRegisterRequest(BaseModel):
    """Owner registration request"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=15)
    password: str = Field(..., min_length=8, max_length=128)
    company_name: str = Field(..., min_length=1, max_length=200)
    company_code: str = Field(..., min_length=1, max_length=20)

    @validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class OwnerRegisterResponse(BaseModel):
    """Owner registration response"""
    user_id: int
    email: str
    first_name: str
    last_name: str
    company_id: str
    company_name: str
    message: str


# ─── Login ───────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    """Login request (all roles)"""
    email: EmailStr
    password: str
    totp_code: Optional[str] = None


class CompanyInfo(BaseModel):
    """Company information"""
    company_id: str
    company_name: str
    company_code: str
    role: CompanyRoleEnum
    branch_id: Optional[str] = None
    branch_name: Optional[str] = None


class UserProfile(BaseModel):
    """User profile"""
    user_id: int
    email: str
    first_name: str
    last_name: str
    display_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    is_owner: bool
    is_two_factor_enabled: bool
    status: str


class LoginResponse(BaseModel):
    """Login response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserProfile
    company: CompanyInfo
    expires_in: int


# ─── Token ───────────────────────────────────────────────────────────────────

class TokenRefreshRequest(BaseModel):
    """Token refresh request"""
    refresh_token: str


class TokenRefreshResponse(BaseModel):
    """Token refresh response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


# ─── Password Management ─────────────────────────────────────────────────────

class ChangePasswordRequest(BaseModel):
    """Change password request"""
    current_password: str
    new_password: str
    confirm_password: str

    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


class ForgotPasswordRequest(BaseModel):
    """Forgot password request"""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Reset password request"""
    token: str
    new_password: str
    confirm_password: str

    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


# ─── 2FA ─────────────────────────────────────────────────────────────────────

class Enable2FARequest(BaseModel):
    """Enable 2FA request"""
    password: str


class Enable2FAResponse(BaseModel):
    """Enable 2FA response"""
    secret: str
    qr_code: str
    backup_codes: List[str]


class Confirm2FARequest(BaseModel):
    """Confirm 2FA request"""
    totp_code: str


class Disable2FARequest(BaseModel):
    """Disable 2FA request"""
    password: str
    totp_code: str


# ─── Company Management ──────────────────────────────────────────────────────

class CreateCompanyRequest(BaseModel):
    """Create company request"""
    company_name: str = Field(..., min_length=1, max_length=200)
    company_code: str = Field(..., min_length=1, max_length=20)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    pan: Optional[str] = None
    gstin: Optional[str] = None
    cin: Optional[str] = None


class CompanyOut(BaseModel):
    """Company output"""
    company_id: str
    company_name: str
    company_code: str
    email: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Team Management ────────────────────────────────────────────────────────

class AddTeamMemberRequest(BaseModel):
    """Add team member request"""
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = None
    role: CompanyRoleEnum
    branch_id: Optional[str] = None


class TeamMemberOut(BaseModel):
    """Team member output"""
    company_user_id: str
    user_id: int
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    role: CompanyRoleEnum
    status: str
    joined_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ─── Client Management ──────────────────────────────────────────────────────

class AddClientRequest(BaseModel):
    """Add client request"""
    client_name: str = Field(..., min_length=1, max_length=200)
    client_code: str = Field(..., min_length=1, max_length=20)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    client_type: Optional[str] = None
    pan: Optional[str] = None
    gstin: Optional[str] = None


class ClientOut(BaseModel):
    """Client output"""
    client_id: str
    client_name: str
    client_code: str
    email: Optional[str] = None
    phone: Optional[str] = None
    client_type: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Branch Management ──────────────────────────────────────────────────────

class CreateBranchRequest(BaseModel):
    """Create branch request"""
    branch_name: str = Field(..., min_length=1, max_length=200)
    branch_code: str = Field(..., min_length=1, max_length=20)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    is_head_office: bool = False
    manager_id: Optional[int] = None


class BranchOut(BaseModel):
    """Branch output"""
    branch_id: str
    branch_name: str
    branch_code: str
    city: Optional[str] = None
    state: Optional[str] = None
    is_head_office: bool
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Error Response ─────────────────────────────────────────────────────────

class ErrorResponse(BaseModel):
    """Error response"""
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ─── Change Company/Branch ──────────────────────────────────────────────────

class ChangeCompanyBranchRequest(BaseModel):
    """Change company and branch request"""
    company_id: str
    branch_id: Optional[str] = None


class ChangeCompanyBranchResponse(BaseModel):
    """Change company and branch response"""
    message: str
    company: CompanyInfo

