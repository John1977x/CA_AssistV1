from sqlalchemy import (
    BigInteger, Boolean, Column, Date, DateTime, ForeignKey,
    Integer, Numeric, SmallInteger, String, Text, ARRAY,
    func, text
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime, date
from typing import Optional, List
import uuid
from app.db.session import Base


# ─── Subscription ────────────────────────────────────────────────────────────

class Subscription(Base):
    __tablename__ = "subscription"

    subscription_id     = Column(Integer, primary_key=True, autoincrement=True)
    plan_name           = Column(String(100), nullable=False)
    plan_code           = Column(String(20), nullable=False, unique=True)
    description         = Column(Text)
    price_monthly       = Column(Numeric(10, 2), nullable=False)
    price_yearly        = Column(Numeric(10, 2))
    max_users           = Column(Integer, nullable=False, default=5)
    max_clients         = Column(Integer)
    max_branches        = Column(Integer, nullable=False, default=1)
    storage_limit_gb    = Column(Numeric(6, 2))
    features_json       = Column(JSONB)
    is_active           = Column(Boolean, nullable=False, default=True)
    trial_days          = Column(Integer, nullable=False, default=14)
    sort_order          = Column(Integer, nullable=False, default=0)
    created_at          = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at          = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    created_by          = Column(Integer)

    tenants             = relationship("Tenant", back_populates="subscription")
    history             = relationship("SubscriptionHistory", foreign_keys="SubscriptionHistory.subscription_id", back_populates="subscription")


# ─── SubscriptionHistory ─────────────────────────────────────────────────────

class SubscriptionHistory(Base):
    __tablename__ = "subscription_history"

    history_id              = Column(BigInteger, primary_key=True, autoincrement=True)
    tenant_id               = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False)
    subscription_id         = Column(Integer, ForeignKey("subscription.subscription_id"), nullable=False)
    previous_subscription_id= Column(Integer, ForeignKey("subscription.subscription_id"))
    action                  = Column(String(30), nullable=False)  # NEW, UPGRADE, DOWNGRADE, RENEW, CANCEL, TRIAL
    start_date              = Column(Date, nullable=False)
    end_date                = Column(Date, nullable=False)
    billing_cycle           = Column(String(10), nullable=False, default="MONTHLY")
    amount_paid             = Column(Numeric(10, 2))
    payment_method          = Column(String(50))
    transaction_ref         = Column(String(100))
    invoice_number          = Column(String(50))
    is_active               = Column(Boolean, nullable=False, default=True)
    notes                   = Column(Text)
    created_at              = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_by              = Column(Integer)

    tenant       = relationship("Tenant", back_populates="subscription_history")
    subscription = relationship("Subscription", foreign_keys=[subscription_id], back_populates="history")


# ─── Tenant ──────────────────────────────────────────────────────────────────

class Tenant(Base):
    __tablename__ = "tenant"

    tenant_id               = Column(Integer, primary_key=True, autoincrement=True)
    subscription_id         = Column(Integer, ForeignKey("subscription.subscription_id"), nullable=False)
    tenant_code             = Column(String(30), nullable=False, unique=True)
    firm_name               = Column(String(200), nullable=False)
    owner_name              = Column(String(150), nullable=False)
    email                   = Column(String(150), nullable=False, unique=True)
    phone                   = Column(String(15), nullable=False)
    alternate_phone         = Column(String(15))
    membership_number       = Column(String(50))
    gstin                   = Column(String(15))
    pan                     = Column(String(10))
    address_line1           = Column(String(250))
    address_line2           = Column(String(250))
    city                    = Column(String(100))
    state                   = Column(String(100))
    pincode                 = Column(String(10))
    country                 = Column(String(100), nullable=False, default="India")
    logo_url                = Column(Text)
    timezone                = Column(String(60), nullable=False, default="Asia/Kolkata")
    currency_code           = Column(String(3), nullable=False, default="INR")
    financial_year_start    = Column(SmallInteger, nullable=False, default=4)
    status                  = Column(String(20), nullable=False, default="ACTIVE")
    trial_end_date          = Column(Date)
    onboarded_at            = Column(DateTime(timezone=True))
    last_login_at           = Column(DateTime(timezone=True))
    created_at              = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at              = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    is_deleted              = Column(Boolean, nullable=False, default=False)

    subscription            = relationship("Subscription", back_populates="tenants")
    subscription_history    = relationship("SubscriptionHistory", back_populates="tenant")
    users                   = relationship("User", back_populates="tenant")
    roles                   = relationship("UserRole", back_populates="tenant")
    branches                = relationship("Branch", back_populates="tenant")


# ─── UserRole ────────────────────────────────────────────────────────────────

class UserRole(Base):
    __tablename__ = "user_role"

    role_id             = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id           = Column(Integer, ForeignKey("tenant.tenant_id"))   # NULL = system role
    role_name           = Column(String(100), nullable=False)
    role_code           = Column(String(30), nullable=False)
    description         = Column(Text)
    permissions_json    = Column(JSONB, nullable=False, default={})
    is_system_role      = Column(Boolean, nullable=False, default=False)
    can_manage_users    = Column(Boolean, nullable=False, default=False)
    can_view_billing    = Column(Boolean, nullable=False, default=False)
    can_approve_task    = Column(Boolean, nullable=False, default=False)
    is_active           = Column(Boolean, nullable=False, default=True)
    sort_order          = Column(Integer, nullable=False, default=0)
    created_at          = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at          = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    tenant              = relationship("Tenant", back_populates="roles")
    users               = relationship("User", back_populates="role")


# ─── Branch ──────────────────────────────────────────────────────────────────

class Branch(Base):
    __tablename__ = "branch"

    branch_id           = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id           = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False)
    branch_name         = Column(String(150), nullable=False)
    branch_code         = Column(String(20), nullable=False)
    manager_user_id     = Column(Integer, ForeignKey("user.user_id"))
    email               = Column(String(150))
    phone               = Column(String(15))
    address_line1       = Column(String(250))
    address_line2       = Column(String(250))
    city                = Column(String(100))
    state               = Column(String(100))
    pincode             = Column(String(10))
    gstin               = Column(String(15))
    is_head_office      = Column(Boolean, nullable=False, default=False)
    is_active           = Column(Boolean, nullable=False, default=True)
    created_at          = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at          = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    tenant              = relationship("Tenant", back_populates="branches")
    manager             = relationship("User", foreign_keys=[manager_user_id])
    users               = relationship("User", foreign_keys="User.branch_id", back_populates="branch")


# ─── User ────────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "user"

    user_id                 = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id               = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False)
    role_id                 = Column(Integer, ForeignKey("user_role.role_id"), nullable=False)
    branch_id               = Column(Integer, ForeignKey("branch.branch_id"))
    first_name              = Column(String(100), nullable=False)
    last_name               = Column(String(100), nullable=False)
    display_name            = Column(String(200))
    email                   = Column(String(150), nullable=False, unique=True)
    phone                   = Column(String(15))
    password_hash           = Column(Text, nullable=False)
    avatar_url              = Column(Text)
    designation             = Column(String(100))
    membership_number       = Column(String(50))
    is_owner                = Column(Boolean, nullable=False, default=False)
    is_two_factor_enabled   = Column(Boolean, nullable=False, default=False)
    two_factor_secret       = Column(Text)
    last_login_at           = Column(DateTime(timezone=True))
    last_login_ip           = Column(String(45))
    password_changed_at     = Column(DateTime(timezone=True))
    failed_login_attempts   = Column(Integer, nullable=False, default=0)
    locked_until            = Column(DateTime(timezone=True))
    status                  = Column(String(20), nullable=False, default="ACTIVE")
    invite_token            = Column(String(100))
    invite_expiry           = Column(DateTime(timezone=True))
    reset_token             = Column(String(100))
    reset_expiry            = Column(DateTime(timezone=True))
    notification_prefs_json = Column(JSONB)
    created_at              = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at              = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    is_deleted              = Column(Boolean, nullable=False, default=False)

    tenant                  = relationship("Tenant", back_populates="users")
    role                    = relationship("UserRole", back_populates="users")
    branch                  = relationship("Branch", foreign_keys=[branch_id], back_populates="users")
    logs                    = relationship("UserLog", back_populates="user")
    # New relationships for multi-company architecture
    owned_companies         = relationship("Company", back_populates="owner", foreign_keys="Company.owner_id")
    company_users           = relationship("CompanyUser", back_populates="user")


# ─── UserLog ─────────────────────────────────────────────────────────────────

class UserLog(Base):
    __tablename__ = "user_log"

    log_id          = Column(BigInteger, primary_key=True, autoincrement=True)
    tenant_id       = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False)
    user_id         = Column(Integer, ForeignKey("user.user_id"))
    action          = Column(String(100), nullable=False)
    module          = Column(String(60), nullable=False)
    entity_type     = Column(String(60))
    entity_id       = Column(Integer)
    old_value_json  = Column(JSONB)
    new_value_json  = Column(JSONB)
    ip_address      = Column(String(45))
    user_agent      = Column(Text)
    session_id      = Column(String(100))
    is_success      = Column(Boolean, nullable=False, default=True)
    error_message   = Column(Text)
    duration_ms     = Column(Integer)
    created_at      = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    user            = relationship("User", back_populates="logs")
