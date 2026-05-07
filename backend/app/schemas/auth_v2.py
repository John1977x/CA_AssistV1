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
    company_id: Optional[str] = None
    company_name: Optional[str] = None
    company_code: Optional[str] = None
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
    
    @classmethod
    def from_orm(cls, obj):
        """Convert ORM object to schema, converting UUID to string"""
        if obj is None:
            return None
        data = {
            'company_id': str(obj.company_id) if hasattr(obj, 'company_id') else None,
            'company_name': obj.company_name if hasattr(obj, 'company_name') else None,
            'company_code': obj.company_code if hasattr(obj, 'company_code') else None,
            'email': obj.email if hasattr(obj, 'email') else None,
            'phone': obj.phone if hasattr(obj, 'phone') else None,
            'city': obj.city if hasattr(obj, 'city') else None,
            'state': obj.state if hasattr(obj, 'state') else None,
            'status': obj.status if hasattr(obj, 'status') else None,
            'created_at': obj.created_at if hasattr(obj, 'created_at') else None,
        }
        return cls(**data)


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
    
    @classmethod
    def from_orm(cls, obj):
        """Convert ORM object to schema, converting UUID to string"""
        if obj is None:
            return None
        # Get user details from the relationship (should be eagerly loaded)
        user = obj.user if hasattr(obj, 'user') else None
        role = obj.role if hasattr(obj, 'role') else None
        
        # Extract role name - handle both CompanyRole object and string
        role_name = None
        if role:
            if hasattr(role, 'role_name'):
                role_name = role.role_name
            elif isinstance(role, str):
                role_name = role
        
        data = {
            'company_user_id': str(obj.company_user_id) if hasattr(obj, 'company_user_id') else None,
            'user_id': obj.user_id if hasattr(obj, 'user_id') else None,
            'first_name': user.first_name if user and hasattr(user, 'first_name') else None,
            'last_name': user.last_name if user and hasattr(user, 'last_name') else None,
            'email': user.email if user and hasattr(user, 'email') else None,
            'phone': user.phone if user and hasattr(user, 'phone') else None,
            'role': role_name,
            'status': obj.status if hasattr(obj, 'status') else None,
            'joined_at': obj.joined_at if hasattr(obj, 'joined_at') else None,
        }
        return cls(**data)


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
    
    @classmethod
    def from_orm(cls, obj):
        """Convert ORM object to schema, converting UUID to string"""
        if obj is None:
            return None
        data = {
            'client_id': str(obj.client_id) if hasattr(obj, 'client_id') else None,
            'client_name': obj.client_name if hasattr(obj, 'client_name') else None,
            'client_code': obj.client_code if hasattr(obj, 'client_code') else None,
            'email': obj.email if hasattr(obj, 'email') else None,
            'phone': obj.phone if hasattr(obj, 'phone') else None,
            'client_type': obj.client_type if hasattr(obj, 'client_type') else None,
            'status': obj.status if hasattr(obj, 'status') else None,
            'created_at': obj.created_at if hasattr(obj, 'created_at') else None,
        }
        return cls(**data)


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
    
    @classmethod
    def from_orm(cls, obj):
        """Convert ORM object to schema, converting UUID to string"""
        if obj is None:
            return None
        data = {
            'branch_id': str(obj.branch_id) if hasattr(obj, 'branch_id') else None,
            'branch_name': obj.branch_name if hasattr(obj, 'branch_name') else None,
            'branch_code': obj.branch_code if hasattr(obj, 'branch_code') else None,
            'city': obj.city if hasattr(obj, 'city') else None,
            'state': obj.state if hasattr(obj, 'state') else None,
            'is_head_office': obj.is_head_office if hasattr(obj, 'is_head_office') else False,
            'status': obj.status if hasattr(obj, 'status') else None,
            'created_at': obj.created_at if hasattr(obj, 'created_at') else None,
        }
        return cls(**data)


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



# ─── Document Request Tickets ──────────────────────────────────────────────

class DocumentRequestTicketCreate(BaseModel):
    """Create document request ticket"""
    document_types: List[str] = Field(..., min_items=1)  # ["PAN", "TAN", "COMPANY_ESTABLISHED_DATE"]
    description: Optional[str] = None
    priority: str = Field(default="NORMAL", pattern="^(URGENT|NORMAL|LOW)$")


class DocumentRequestTicketUpdate(BaseModel):
    """Update document request ticket"""
    status: Optional[str] = None  # OPEN, IN_PROGRESS, COMPLETED, REJECTED
    assigned_to_user_id: Optional[int] = None
    completion_notes: Optional[str] = None


class DocumentRequestTicketOut(BaseModel):
    """Document request ticket output"""
    ticket_id: str
    company_id: str
    client_id: str
    requested_by_user_id: int
    document_types: List[str]
    description: Optional[str] = None
    priority: str
    status: str
    assigned_to_user_id: Optional[int] = None
    completed_at: Optional[datetime] = None
    completed_by_user_id: Optional[int] = None
    completion_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm(cls, obj):
        """Convert ORM object to schema, converting UUID to string"""
        if obj is None:
            return None
        data = {
            'ticket_id': str(obj.ticket_id) if hasattr(obj, 'ticket_id') else None,
            'company_id': str(obj.company_id) if hasattr(obj, 'company_id') else None,
            'client_id': str(obj.client_id) if hasattr(obj, 'client_id') else None,
            'requested_by_user_id': obj.requested_by_user_id if hasattr(obj, 'requested_by_user_id') else None,
            'document_types': obj.document_types if hasattr(obj, 'document_types') else [],
            'description': obj.description if hasattr(obj, 'description') else None,
            'priority': obj.priority if hasattr(obj, 'priority') else None,
            'status': obj.status if hasattr(obj, 'status') else None,
            'assigned_to_user_id': obj.assigned_to_user_id if hasattr(obj, 'assigned_to_user_id') else None,
            'completed_at': obj.completed_at if hasattr(obj, 'completed_at') else None,
            'completed_by_user_id': obj.completed_by_user_id if hasattr(obj, 'completed_by_user_id') else None,
            'completion_notes': obj.completion_notes if hasattr(obj, 'completion_notes') else None,
            'created_at': obj.created_at if hasattr(obj, 'created_at') else None,
            'updated_at': obj.updated_at if hasattr(obj, 'updated_at') else None,
        }
        return cls(**data)
