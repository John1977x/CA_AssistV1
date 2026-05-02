from pydantic import BaseModel, Field, UUID4
from typing import Optional
from datetime import date, datetime


# ─── Customer Event Schemas ──────────────────────────────────────────────────

class CustomerEventBase(BaseModel):
    event_type: str = Field(..., max_length=20)  # BIRTHDAY / ANNIVERSARY / CUSTOM
    event_date: date
    recurring_yearly: bool = True
    is_active: bool = True


class CustomerEventCreate(CustomerEventBase):
    customer_id: int
    tenant_id: int


class CustomerEventUpdate(BaseModel):
    event_type: Optional[str] = Field(None, max_length=20)
    event_date: Optional[date] = None
    recurring_yearly: Optional[bool] = None
    is_active: Optional[bool] = None


class CustomerEventResponse(CustomerEventBase):
    event_id: UUID4
    customer_id: int
    tenant_id: int
    last_triggered_year: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Customer Event Notification Schemas ─────────────────────────────────────

class CustomerEventNotificationBase(BaseModel):
    channel: str = Field(..., max_length=20)  # EMAIL / WHATSAPP / SMS
    scheduled_at: datetime
    status: str = Field('Pending', max_length=20)


class CustomerEventNotificationCreate(CustomerEventNotificationBase):
    event_id: UUID4
    customer_id: int
    tenant_id: int
    template_id: Optional[UUID4] = None
    wa_template_id: Optional[UUID4] = None


class CustomerEventNotificationUpdate(BaseModel):
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    status: Optional[str] = Field(None, max_length=20)


class CustomerEventNotificationResponse(CustomerEventNotificationBase):
    notification_id: UUID4
    event_id: UUID4
    customer_id: int
    tenant_id: int
    template_id: Optional[UUID4]
    wa_template_id: Optional[UUID4]
    sent_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
