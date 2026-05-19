"""
Notification Endpoints - API routes for notifications
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user
from app.models.auth import User
from app.schemas.notification import (
    NotificationCreate, NotificationUpdate, NotificationOut,
    NotificationListResponse, NotificationPreferenceOut,
    NotificationPreferenceUpdate
)
from app.services.notification import (
    create_notification, get_notification, get_user_notifications,
    mark_as_read, mark_all_as_read, archive_notification,
    delete_notification, get_or_create_preference, update_preference,
    get_unread_count
)

router = APIRouter(prefix="/notifications", tags=["Notifications"])


# ─── Notification Endpoints ──────────────────────────────────────────────────

@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str = Query(None),
):
    """Get paginated notifications for current user"""
    return await get_user_notifications(db, current_user.user_id, page, page_size, status)


@router.get("/unread-count", response_model=dict)
async def get_unread_notification_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get count of unread notifications"""
    count = await get_unread_count(db, current_user.user_id)
    return {"unread_count": count}


@router.get("/{notification_id}", response_model=NotificationOut)
async def get_single_notification(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single notification"""
    notification = await get_notification(db, notification_id)
    # Verify ownership
    if notification.user_id != current_user.user_id:
        from app.core.errors import AuthorizationError
        raise AuthorizationError("You don't have access to this notification")
    return notification


@router.post("/{notification_id}/read", response_model=NotificationOut)
async def mark_notification_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a notification as read"""
    notification = await get_notification(db, notification_id)
    # Verify ownership
    if notification.user_id != current_user.user_id:
        from app.core.errors import AuthorizationError
        raise AuthorizationError("You don't have access to this notification")
    return await mark_as_read(db, notification_id)


@router.post("/read-all", response_model=dict)
async def mark_all_notifications_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark all unread notifications as read"""
    return await mark_all_as_read(db, current_user.user_id)


@router.post("/{notification_id}/archive", response_model=NotificationOut)
async def archive_single_notification(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Archive a notification"""
    notification = await get_notification(db, notification_id)
    # Verify ownership
    if notification.user_id != current_user.user_id:
        from app.core.errors import AuthorizationError
        raise AuthorizationError("You don't have access to this notification")
    return await archive_notification(db, notification_id)


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_single_notification(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a notification"""
    notification = await get_notification(db, notification_id)
    # Verify ownership
    if notification.user_id != current_user.user_id:
        from app.core.errors import AuthorizationError
        raise AuthorizationError("You don't have access to this notification")
    await delete_notification(db, notification_id)


# ─── Notification Preference Endpoints ───────────────────────────────────────

@router.get("/preferences/me", response_model=NotificationPreferenceOut)
async def get_my_preferences(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current user's notification preferences"""
    return await get_or_create_preference(db, current_user.user_id)


@router.put("/preferences/me", response_model=NotificationPreferenceOut)
async def update_my_preferences(
    data: NotificationPreferenceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update current user's notification preferences"""
    return await update_preference(db, current_user.user_id, data)
