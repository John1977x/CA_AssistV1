"""
Notification Models - For user notifications and alerts
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum as SQLEnum, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timezone
import enum

from app.db.session import Base


class NotificationTypeEnum(str, enum.Enum):
    """Types of notifications"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    TASK_ASSIGNED = "task_assigned"
    TASK_COMPLETED = "task_completed"
    DOCUMENT_REQUEST = "document_request"
    ASSIGNMENT_SUBMITTED = "assignment_submitted"
    TICKET_CREATED = "ticket_created"
    TICKET_UPDATED = "ticket_updated"
    USER_INVITED = "user_invited"
    COMPANY_CREATED = "company_created"
    SUBSCRIPTION_UPDATED = "subscription_updated"


class NotificationStatusEnum(str, enum.Enum):
    """Status of notifications"""
    UNREAD = "unread"
    READ = "read"
    ARCHIVED = "archived"


class Notification(Base):
    """
    User Notifications - Stores all notifications for users
    """
    __tablename__ = "notification"

    notification_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False, index=True)
    
    # Notification details
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(SQLEnum(NotificationTypeEnum), nullable=False, default=NotificationTypeEnum.INFO)
    status = Column(SQLEnum(NotificationStatusEnum), nullable=False, default=NotificationStatusEnum.UNREAD)
    
    # Related entity (for linking to tasks, tickets, etc.)
    related_entity_type = Column(String(50))  # "task", "ticket", "assignment", "document_request", etc.
    related_entity_id = Column(Integer)  # ID of the related entity
    
    # Action URL (where to navigate when clicked)
    action_url = Column(String(500))
    
    # Additional data (JSON for flexibility)
    metadata = Column(JSONB, default={})
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    read_at = Column(DateTime(timezone=True))
    archived_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])

    def __repr__(self):
        return f"<Notification {self.notification_id}: {self.title}>"


class NotificationPreference(Base):
    """
    User Notification Preferences - Controls which notifications to receive
    """
    __tablename__ = "notification_preference"

    preference_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False, unique=True, index=True)
    
    # Notification type preferences (enabled/disabled)
    task_assigned = Column(Boolean, nullable=False, default=True)
    task_completed = Column(Boolean, nullable=False, default=True)
    document_request = Column(Boolean, nullable=False, default=True)
    assignment_submitted = Column(Boolean, nullable=False, default=True)
    ticket_created = Column(Boolean, nullable=False, default=True)
    ticket_updated = Column(Boolean, nullable=False, default=True)
    user_invited = Column(Boolean, nullable=False, default=True)
    company_created = Column(Boolean, nullable=False, default=True)
    subscription_updated = Column(Boolean, nullable=False, default=True)
    
    # Delivery preferences
    email_notifications = Column(Boolean, nullable=False, default=True)
    in_app_notifications = Column(Boolean, nullable=False, default=True)
    
    # Quiet hours (don't send notifications between these times)
    quiet_hours_enabled = Column(Boolean, nullable=False, default=False)
    quiet_hours_start = Column(String(5))  # HH:MM format
    quiet_hours_end = Column(String(5))    # HH:MM format
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])

    def __repr__(self):
        return f"<NotificationPreference {self.preference_id}: user_id={self.user_id}>"
