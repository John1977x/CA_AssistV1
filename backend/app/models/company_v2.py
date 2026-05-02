"""
New Company Models for Multi-Company, Multi-Role Architecture
"""

from sqlalchemy import (
    Boolean, Column, Date, DateTime, ForeignKey,
    Integer, String, Text, func, ARRAY, Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.session import Base
import uuid
import enum


class CompanyRoleEnum(str, enum.Enum):
    """Company roles"""
    OWNER = "OWNER"
    MANAGER = "MANAGER"
    EMPLOYEE = "EMPLOYEE"
    CLIENT = "CLIENT"


class CompanyStatusEnum(str, enum.Enum):
    """Company status"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"


class UserStatusEnum(str, enum.Enum):
    """User status in company"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    INVITED = "INVITED"
    SUSPENDED = "SUSPENDED"


class Company(Base):
    """
    Company - Represents a company owned by an owner
    An owner can have multiple companies
    """
    __tablename__ = "company"

    company_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(Integer, ForeignKey("user.user_id"), nullable=False, index=True)
    company_name = Column(String(200), nullable=False, index=True)
    company_code = Column(String(20), nullable=False, unique=True, index=True)
    email = Column(String(150))
    phone = Column(String(20))
    address_line1 = Column(String(200))
    address_line2 = Column(String(200))
    city = Column(String(100))
    state = Column(String(100))
    pincode = Column(String(10))
    country = Column(String(100), default="India")
    pan = Column(String(10))
    gstin = Column(String(15))
    cin = Column(String(21))
    status = Column(SQLEnum(CompanyStatusEnum), nullable=False, default=CompanyStatusEnum.ACTIVE)
    description = Column(Text)
    logo_url = Column(String(500))
    website = Column(String(200))
    extra_data = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, nullable=False, default=False)

    # Relationships
    owner = relationship("User", foreign_keys=[owner_id], back_populates="owned_companies")
    branches = relationship("CompanyBranch", back_populates="company", cascade="all, delete-orphan")
    company_users = relationship("CompanyUser", back_populates="company", cascade="all, delete-orphan")
    company_clients = relationship("CompanyClient", back_populates="company", cascade="all, delete-orphan")
    company_roles = relationship("CompanyRole", back_populates="company", cascade="all, delete-orphan")


class CompanyBranch(Base):
    """
    Company Branch - Represents a branch of a company
    A company can have multiple branches
    """
    __tablename__ = "company_branch"

    branch_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("company.company_id"), nullable=False, index=True)
    manager_id = Column(Integer, ForeignKey("user.user_id"))
    branch_name = Column(String(200), nullable=False, index=True)
    branch_code = Column(String(20), nullable=False)
    email = Column(String(150))
    phone = Column(String(20))
    address_line1 = Column(String(200))
    address_line2 = Column(String(200))
    city = Column(String(100))
    state = Column(String(100))
    pincode = Column(String(10))
    country = Column(String(100), default="India")
    is_head_office = Column(Boolean, nullable=False, default=False)
    status = Column(SQLEnum(CompanyStatusEnum), nullable=False, default=CompanyStatusEnum.ACTIVE)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, nullable=False, default=False)

    # Relationships
    company = relationship("Company", back_populates="branches")
    manager = relationship("User", foreign_keys=[manager_id])


class CompanyRole(Base):
    """
    Company Role - Defines roles within a company
    Each company has its own set of roles (Owner, Manager, Employee, Client)
    """
    __tablename__ = "company_role"

    role_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("company.company_id"), nullable=False, index=True)
    role_name = Column(SQLEnum(CompanyRoleEnum), nullable=False)
    description = Column(Text)
    permissions = Column(JSONB, default={})  # {tasks: true, clients: true, team: true, ...}
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    company = relationship("Company", back_populates="company_roles")
    company_users = relationship("CompanyUser", back_populates="role")


class CompanyUser(Base):
    """
    Company User - Maps users to companies with their role
    A user can be associated with multiple companies in different roles
    """
    __tablename__ = "company_user"

    company_user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("company.company_id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False, index=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey("company_role.role_id"), nullable=False)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("company_branch.branch_id"))
    status = Column(SQLEnum(UserStatusEnum), nullable=False, default=UserStatusEnum.ACTIVE)
    invited_at = Column(DateTime(timezone=True))
    joined_at = Column(DateTime(timezone=True))
    invite_token = Column(String(500))
    invite_token_expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, nullable=False, default=False)

    # Relationships
    company = relationship("Company", back_populates="company_users")
    user = relationship("User", back_populates="company_users")
    role = relationship("CompanyRole", back_populates="company_users")
    branch = relationship("CompanyBranch")


class CompanyClient(Base):
    """
    Company Client - Represents clients/customers of a company
    A company can have multiple clients
    """
    __tablename__ = "company_client"

    client_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("company.company_id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("user.user_id"))  # If client has login
    client_name = Column(String(200), nullable=False, index=True)
    client_code = Column(String(20), nullable=False)
    email = Column(String(150))
    phone = Column(String(20))
    alternate_phone = Column(String(20))
    whatsapp = Column(String(20))
    address_line1 = Column(String(200))
    address_line2 = Column(String(200))
    city = Column(String(100))
    state = Column(String(100))
    pincode = Column(String(10))
    country = Column(String(100), default="India")
    pan = Column(String(10))
    gstin = Column(String(15))
    cin = Column(String(21))
    client_type = Column(String(50))  # INDIVIDUAL, PARTNERSHIP, COMPANY, etc.
    status = Column(String(20), nullable=False, default="ACTIVE")
    assigned_manager_id = Column(Integer, ForeignKey("user.user_id"))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, nullable=False, default=False)

    # Relationships
    company = relationship("Company", back_populates="company_clients")
    user = relationship("User", foreign_keys=[user_id])
    assigned_manager = relationship("User", foreign_keys=[assigned_manager_id])
