"""
Notification Service - Handles notification operations
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, desc, and_
from datetime import datetime, timezone
from typing import Optional, List, Tuple

from app.models.notification import Notification, NotificationPreference, NotificationTypeEnum, NotificationStatusEnum
from app.models.auth import User
from app.schemas.notification import (
    NotificationCreate, NotificationUpdate, NotificationOut,
    NotificationPreferenceOut, NotificationPreferenceUpdate,
    NotificationListResponse
)
from app.core.errors import ResourceNotFoundError, ValidationError


# ─── Notification CRUD ───────────────────────────────────────────────────────

async def create_notification(
    db: AsyncSession,
    user_id: int,
    data: NotificationCreate
) -> NotificationOut:
    """Create a new notification for a user"""
    # Verify user exists
    user_result = await db.execute(select(User).where(User.user_id == user_id))
    if not user_result.scalar_one_or_none():
        raise ResourceNotFoundError("User")

    notification = Notification(
        user_id=user_id,
        title=data.title,
        message=data.message,
        notification_type=data.notification_type,
        related_entity_type=data.related_entity_type,
        related_entity_id=data.related_entity_id,
        action_url=data.action_url,
        metadata=data.metadata or {},
    )
    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    return NotificationOut.model_validate(notification)


async def get_notification(db: AsyncSession, notification_id: int) -> NotificationOut:
    """Get a single notification"""
    result = await db.execute(
        select(Notification).where(Notification.notification_id == notification_id)
    )
    notification = result.scalar_one_or_none()
    if not notification:
        raise ResourceNotFoundError("Notification")
    return NotificationOut.model_validate(notification)


async def get_user_notifications(
    db: AsyncSession,
    user_id: int,
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = None,
) -> NotificationListResponse:
    """Get paginated notifications for a user"""
    # Verify user exists
    user_result = await db.execute(select(User).where(User.user_id == user_id))
    if not user_result.scalar_one_or_none():
        raise ResourceNotFoundError("User")

    # Build query
    query = select(Notification).where(Notification.user_id == user_id)
    
    # Filter by status if provided
    if status:
        query = query.where(Notification.status == status)
    
    # Order by created_at descending (newest first)
    query = query.order_by(desc(Notification.created_at))
    
    # Get total count
    count_result = await db.execute(
        select(func.count(Notification.notification_id)).where(Notification.user_id == user_id)
    )
    total = count_result.scalar() or 0
    
    # Get unread count
    unread_result = await db.execute(
        select(func.count(Notification.notification_id)).where(
            and_(
                Notification.user_id == user_id,
                Notification.status == NotificationStatusEnum.UNREAD
            )
        )
    )
    unread_count = unread_result.scalar() or 0
    
    # Paginate
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    result = await db.execute(query)
    notifications = result.scalars().all()
    
    return NotificationListResponse(
        notifications=[NotificationOut.model_validate(n) for n in notifications],
        total=total,
        unread_count=unread_count,
        page=page,
        page_size=page_size,
    )


async def mark_as_read(db: AsyncSession, notification_id: int) -> NotificationOut:
    """Mark a notification as read"""
    notification = await db.execute(
        select(Notification).where(Notification.notification_id == notification_id)
    )
    notification = notification.scalar_one_or_none()
    if not notification:
        raise ResourceNotFoundError("Notification")
    
    notification.status = NotificationStatusEnum.READ
    notification.read_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(notification)
    return NotificationOut.model_validate(notification)


async def mark_all_as_read(db: AsyncSession, user_id: int) -> dict:
    """Mark all unread notifications as read for a user"""
    # Verify user exists
    user_result = await db.execute(select(User).where(User.user_id == user_id))
    if not user_result.scalar_one_or_none():
        raise ResourceNotFoundError("User")
    
    # Update all unread notifications
    await db.execute(
        update(Notification)
        .where(
            and_(
                Notification.user_id == user_id,
                Notification.status == NotificationStatusEnum.UNREAD
            )
        )
        .values(
            status=NotificationStatusEnum.READ,
            read_at=datetime.now(timezone.utc)
        )
    )
    await db.commit()
    
    return {"message": "All notifications marked as read"}


async def archive_notification(db: AsyncSession, notification_id: int) -> NotificationOut:
    """Archive a notification"""
    notification = await db.execute(
        select(Notification).where(Notification.notification_id == notification_id)
    )
    notification = notification.scalar_one_or_none()
    if not notification:
        raise ResourceNotFoundError("Notification")
    
    notification.status = NotificationStatusEnum.ARCHIVED
    notification.archived_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(notification)
    return NotificationOut.model_validate(notification)


async def delete_notification(db: AsyncSession, notification_id: int) -> dict:
    """Delete a notification"""
    notification = await db.execute(
        select(Notification).where(Notification.notification_id == notification_id)
    )
    notification = notification.scalar_one_or_none()
    if not notification:
        raise ResourceNotFoundError("Notification")
    
    await db.delete(notification)
    await db.commit()
    return {"message": "Notification deleted"}


# ─── Notification Preferences ────────────────────────────────────────────────

async def get_or_create_preference(db: AsyncSession, user_id: int) -> NotificationPreferenceOut:
    """Get or create notification preferences for a user"""
    result = await db.execute(
        select(NotificationPreference).where(NotificationPreference.user_id == user_id)
    )
    preference = result.scalar_one_or_none()
    
    if not preference:
        # Verify user exists
        user_result = await db.execute(select(User).where(User.user_id == user_id))
        if not user_result.scalar_one_or_none():
            raise ResourceNotFoundError("User")
        
        # Create default preferences
        preference = NotificationPreference(user_id=user_id)
        db.add(preference)
        await db.commit()
        await db.refresh(preference)
    
    return NotificationPreferenceOut.model_validate(preference)


async def update_preference(
    db: AsyncSession,
    user_id: int,
    data: NotificationPreferenceUpdate
) -> NotificationPreferenceOut:
    """Update notification preferences for a user"""
    preference = await db.execute(
        select(NotificationPreference).where(NotificationPreference.user_id == user_id)
    )
    preference = preference.scalar_one_or_none()
    
    if not preference:
        # Create if doesn't exist
        preference = NotificationPreference(user_id=user_id)
        db.add(preference)
    
    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(preference, field, value)
    
    await db.commit()
    await db.refresh(preference)
    return NotificationPreferenceOut.model_validate(preference)


# ─── Helper Functions ────────────────────────────────────────────────────────

async def should_send_notification(
    db: AsyncSession,
    user_id: int,
    notification_type: NotificationTypeEnum
) -> bool:
    """Check if a notification should be sent based on user preferences"""
    preference = await get_or_create_preference(db, user_id)
    
    # Check if in-app notifications are enabled
    if not preference.in_app_notifications:
        return False
    
    # Check specific notification type preference
    type_map = {
        NotificationTypeEnum.TASK_ASSIGNED: preference.task_assigned,
        NotificationTypeEnum.TASK_COMPLETED: preference.task_completed,
        NotificationTypeEnum.DOCUMENT_REQUEST: preference.document_request,
        NotificationTypeEnum.ASSIGNMENT_SUBMITTED: preference.assignment_submitted,
        NotificationTypeEnum.TICKET_CREATED: preference.ticket_created,
        NotificationTypeEnum.TICKET_UPDATED: preference.ticket_updated,
        NotificationTypeEnum.USER_INVITED: preference.user_invited,
        NotificationTypeEnum.COMPANY_CREATED: preference.company_created,
        NotificationTypeEnum.SUBSCRIPTION_UPDATED: preference.subscription_updated,
    }
    
    return type_map.get(notification_type, True)


async def get_unread_count(db: AsyncSession, user_id: int) -> int:
    """Get count of unread notifications for a user"""
    result = await db.execute(
        select(func.count(Notification.notification_id)).where(
            and_(
                Notification.user_id == user_id,
                Notification.status == NotificationStatusEnum.UNREAD
            )
        )
    )
    return result.scalar() or 0
