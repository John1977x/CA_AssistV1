from sqlalchemy import (
    Boolean, Column, Date, DateTime, ForeignKey,
    Integer, String, Text, func, ARRAY
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
import uuid
from app.db.session import Base


class Ticket(Base):
    """Support tickets raised by clients"""
    __tablename__ = "ticket"

    ticket_id           = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id           = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False)
    customer_id         = Column(Integer, ForeignKey("customer.customer_id"), nullable=False)
    raised_by_user_id   = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    assigned_to_user_id = Column(Integer, ForeignKey("user.user_id"))
    ticket_number       = Column(String(50), nullable=False, unique=True)
    title               = Column(String(300), nullable=False)
    description         = Column(Text, nullable=False)
    category            = Column(String(50), nullable=False)  # TECHNICAL, BILLING, GENERAL, URGENT
    priority            = Column(String(20), nullable=False, default="MEDIUM")  # LOW, MEDIUM, HIGH, URGENT
    status              = Column(String(30), nullable=False, default="OPEN")  # OPEN, IN_PROGRESS, RESOLVED, CLOSED, REOPENED
    resolution          = Column(Text)
    attachments_json    = Column(JSONB)  # Array of file URLs
    tags                = Column(ARRAY(Text))
    created_at          = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at          = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    resolved_at         = Column(DateTime(timezone=True))
    closed_at           = Column(DateTime(timezone=True))
    resolved_by_user_id = Column(Integer, ForeignKey("user.user_id"))
    is_deleted          = Column(Boolean, nullable=False, default=False)

    tenant              = relationship("Tenant")
    customer            = relationship("Customer")
    raised_by           = relationship("User", foreign_keys=[raised_by_user_id])
    assigned_to         = relationship("User", foreign_keys=[assigned_to_user_id])
    resolved_by         = relationship("User", foreign_keys=[resolved_by_user_id])
    comments            = relationship("TicketComment", back_populates="ticket", cascade="all, delete-orphan")


class TicketComment(Base):
    """Comments on tickets"""
    __tablename__ = "ticket_comment"

    comment_id          = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id           = Column(Integer, ForeignKey("ticket.ticket_id"), nullable=False)
    user_id             = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    comment_text        = Column(Text, nullable=False)
    attachments_json    = Column(JSONB)  # Array of file URLs
    is_internal         = Column(Boolean, nullable=False, default=False)  # Internal notes only visible to staff
    created_at          = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at          = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    ticket              = relationship("Ticket", back_populates="comments")
    user                = relationship("User")
