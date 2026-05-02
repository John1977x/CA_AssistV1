from sqlalchemy import (
    Boolean, Column, Date, DateTime, ForeignKey,
    Integer, String, Text, func
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.session import Base
import uuid


class SocialAccount(Base):
    """Social Media Account"""
    __tablename__ = "social_accounts"

    social_account_id   = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id           = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False, index=True)
    platform            = Column(String(20), nullable=False, index=True)  # FACEBOOK / TWITTER / LINKEDIN / INSTAGRAM
    account_name        = Column(String(150), nullable=False)
    account_handle      = Column(String(100))  # e.g. @mycafirm
    access_token        = Column(String(500))  # Encrypted OAuth token
    token_expiry        = Column(DateTime(timezone=True))
    page_id             = Column(String(100))  # Facebook Page ID if applicable
    status              = Column(String(20), nullable=False, default='Active')  # Active / Disconnected / Expired
    connected_at        = Column(DateTime(timezone=True))
    created_at          = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    tenant = relationship("Tenant")
    posts = relationship("SocialPost", back_populates="account")
    schedulers = relationship("SocialScheduler", back_populates="account")


class SocialPostTemplate(Base):
    """Social Post Template"""
    __tablename__ = "social_post_templates"

    post_template_id    = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id           = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False, index=True)
    template_name       = Column(String(150), nullable=False)
    platform            = Column(String(20), nullable=False, index=True)  # FACEBOOK / TWITTER / LINKEDIN / ALL
    category            = Column(String(30))  # PROMOTION / EDUCATION / BIRTHDAY / ANNOUNCEMENT
    content_text        = Column(Text, nullable=False)  # Supports {{ClientName}} tokens
    media_url           = Column(String(500))  # Default image / video
    hashtags            = Column(String(500))  # Space-separated
    is_active           = Column(Boolean, nullable=False, default=True)
    created_at          = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    tenant = relationship("Tenant")
    posts = relationship("SocialPost", back_populates="template")
    schedulers = relationship("SocialScheduler", back_populates="template")


class SocialPost(Base):
    """Social Post"""
    __tablename__ = "social_posts"

    post_id             = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id           = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False, index=True)
    social_account_id   = Column(UUID(as_uuid=True), ForeignKey("social_accounts.social_account_id"), nullable=False, index=True)
    post_template_id    = Column(UUID(as_uuid=True), ForeignKey("social_post_templates.post_template_id"))  # NULL = ad-hoc post
    content_text        = Column(Text, nullable=False)  # Final rendered content
    media_url           = Column(String(500))
    scheduled_at        = Column(DateTime(timezone=True), index=True)  # NULL = post immediately
    published_at        = Column(DateTime(timezone=True))
    platform_post_id    = Column(String(100))  # Returned by FB/Twitter API
    status              = Column(String(20), nullable=False, default='Draft', index=True)  # Draft / Scheduled / Published / Failed
    likes               = Column(Integer, nullable=False, default=0)
    shares              = Column(Integer, nullable=False, default=0)
    reach               = Column(Integer, nullable=False, default=0)
    error_message       = Column(String(300))
    created_at          = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    tenant = relationship("Tenant")
    account = relationship("SocialAccount", back_populates="posts")
    template = relationship("SocialPostTemplate", back_populates="posts")


class SocialScheduler(Base):
    """Social Media Scheduler"""
    __tablename__ = "social_schedulers"

    scheduler_id        = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id           = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False, index=True)
    social_account_id   = Column(UUID(as_uuid=True), ForeignKey("social_accounts.social_account_id"), nullable=False, index=True)
    post_template_id    = Column(UUID(as_uuid=True), ForeignKey("social_post_templates.post_template_id"), nullable=False, index=True)
    trigger_type        = Column(String(20), nullable=False)  # EVENT / CRON / MANUAL
    cron_expression     = Column(String(50))  # e.g. 0 9 * * MON
    trigger_event       = Column(String(50))  # TAX_DEADLINE / BUDGET_DAY etc.
    is_active           = Column(Boolean, nullable=False, default=True)
    last_run_at         = Column(DateTime(timezone=True))
    next_run_at         = Column(DateTime(timezone=True))
    created_at          = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    tenant = relationship("Tenant")
    account = relationship("SocialAccount", back_populates="schedulers")
    template = relationship("SocialPostTemplate", back_populates="schedulers")
