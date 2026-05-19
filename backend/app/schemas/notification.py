"""
Notification Schemas - Request/Response models for notifications
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class NotificationTypeEnum(str, Enum):
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


class NotificationStatusEnum(str, Enum):
    """Status of notifications"""
    UNREAD = "unread"
    READ = "read"
    ARCHIVED = "archived"


class NotificationCreate(BaseModel):
    """Create notification request"""
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1)
    notification_type: NotificationTypeEnum = NotificationTypeEnum.INFO
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[int] = None
    action_url: Optional[str] = None
    metadata: Optional[dict] = None


class NotificationUpdate(BaseModel):
    """Update notification request"""
    status: Optional[NotificationStatusEnum] = None
    read_at: Optional[datetime] = None


class NotificationOut(BaseModel):
    """Notification response"""
    notification_id: int
    user_id: int
    title: str
    message: str
    notification_type: NotificationTypeEnum
    status: NotificationStatusEnum
    related_entity_type: Optional[str]
    related_entity_id: Optional[int]
    action_url: Optional[str]
    metadata: Optional[dict]
    created_at: datetime
    read_at: Optional[datetime]
    archived_at: Optional[datetime]

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """List notifications response"""
    notifications: List[NotificationOut]
    total: int
    unread_count: int
    page: int
    page_size: int


class NotificationPreferenceOut(BaseModel):
    """Notification preference response"""
    preference_id: int
    user_id: int
    task_assigned: bool
    task_completed: bool
    document_request: bool
    assignment_submitted: bool
    ticket_created: bool
    ticket_updated: bool
    user_invited: bool
    company_created: bool
    subscription_updated: bool
    email_notifications: bool
    in_app_notifications: bool
    quiet_hours_enabled: bool
    quiet_hours_start: Optional[str]
    quiet_hours_end: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotificationPreferenceUpdate(BaseModel):
    """Update notification preference request"""
    task_assigned: Optional[bool] = None
    task_completed: Optional[bool] = None
    document_request: Optional[bool] = None
    assignment_submitted: Optional[bool] = None
    ticket_created: Optional[bool] = None
    ticket_updated: Optional[bool] = None
    user_invited: Optional[bool] = None
    company_created: Optional[bool] = None
    subscription_updated: Optional[bool] = None
    email_notifications: Optional[bool] = None
    in_app_notifications: Optional[bool] = None
    quiet_hours_enabled: Optional[bool] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
