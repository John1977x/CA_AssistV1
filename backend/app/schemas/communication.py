from pydantic import BaseModel, Field, UUID4, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime


# ─── Email Template Schemas ──────────────────────────────────────────────────

class EmailTemplateBase(BaseModel):
    template_name: str = Field(..., max_length=150)
    template_code: str = Field(..., max_length=50)
    subject: str = Field(..., max_length=300)
    body_html: str
    variables_json: Optional[Dict[str, Any]] = None
    category: Optional[str] = Field(None, max_length=50)
    is_active: bool = True


class EmailTemplateCreate(EmailTemplateBase):
    tenant_id: int


class EmailTemplateUpdate(BaseModel):
    template_name: Optional[str] = Field(None, max_length=150)
    subject: Optional[str] = Field(None, max_length=300)
    body_html: Optional[str] = None
    variables_json: Optional[Dict[str, Any]] = None
    category: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None


class EmailTemplateResponse(EmailTemplateBase):
    template_id: UUID4
    tenant_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Email Queue Schemas ─────────────────────────────────────────────────────

class EmailQueueBase(BaseModel):
    from_email: EmailStr
    to_email: str = Field(..., max_length=500)
    cc: Optional[str] = Field(None, max_length=500)
    bcc: Optional[str] = Field(None, max_length=500)
    subject: str = Field(..., max_length=300)
    body_html: str
    priority: str = Field('NORMAL', max_length=10)
    scheduled_at: Optional[datetime] = None


class EmailQueueCreate(EmailQueueBase):
    tenant_id: int
    template_id: Optional[UUID4] = None


class EmailQueueUpdate(BaseModel):
    scheduled_at: Optional[datetime] = None
    status: Optional[str] = Field(None, max_length=20)
    error_message: Optional[str] = Field(None, max_length=500)


class EmailQueueResponse(EmailQueueBase):
    queue_id: UUID4
    tenant_id: int
    template_id: Optional[UUID4]
    sent_at: Optional[datetime]
    status: str
    retry_count: int
    error_message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ─── WhatsApp Template Schemas ───────────────────────────────────────────────

class WATemplateBase(BaseModel):
    template_name: str = Field(..., max_length=150)
    template_code: str = Field(..., max_length=50)
    language: str = Field('en', max_length=10)
    category: str = Field(..., max_length=30)
    header_type: Optional[str] = Field(None, max_length=20)
    header_content: Optional[str] = Field(None, max_length=300)
    body_text: str
    footer_text: Optional[str] = Field(None, max_length=300)
    buttons_json: Optional[Dict[str, Any]] = None
    provider_template_id: Optional[str] = Field(None, max_length=100)
    status: str = Field('PENDING', max_length=20)


class WATemplateCreate(WATemplateBase):
    tenant_id: int


class WATemplateUpdate(BaseModel):
    template_name: Optional[str] = Field(None, max_length=150)
    body_text: Optional[str] = None
    footer_text: Optional[str] = Field(None, max_length=300)
    buttons_json: Optional[Dict[str, Any]] = None
    provider_template_id: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field(None, max_length=20)


class WATemplateResponse(WATemplateBase):
    wa_template_id: UUID4
    tenant_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ─── WhatsApp Queue Schemas ──────────────────────────────────────────────────

class WAQueueBase(BaseModel):
    to_phone: str = Field(..., max_length=20)
    variables_json: Optional[Dict[str, Any]] = None
    media_url: Optional[str] = Field(None, max_length=500)
    priority: str = Field('NORMAL', max_length=10)
    scheduled_at: Optional[datetime] = None


class WAQueueCreate(WAQueueBase):
    tenant_id: int
    wa_template_id: UUID4


class WAQueueUpdate(BaseModel):
    scheduled_at: Optional[datetime] = None
    status: Optional[str] = Field(None, max_length=20)
    wa_message_id: Optional[str] = Field(None, max_length=100)
    error_code: Optional[str] = Field(None, max_length=20)
    error_message: Optional[str] = Field(None, max_length=300)


class WAQueueResponse(WAQueueBase):
    wa_queue_id: UUID4
    tenant_id: int
    wa_template_id: UUID4
    sent_at: Optional[datetime]
    status: str
    wa_message_id: Optional[str]
    error_code: Optional[str]
    error_message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Email Scheduler Schemas ─────────────────────────────────────────────────

class EmailSchedulerBase(BaseModel):
    trigger_type: str = Field(..., max_length=20)
    trigger_event: Optional[str] = Field(None, max_length=50)
    cron_expression: Optional[str] = Field(None, max_length=50)
    recipient_type: str = Field(..., max_length=30)
    recipient_filter: Optional[Dict[str, Any]] = None
    is_active: bool = True


class EmailSchedulerCreate(EmailSchedulerBase):
    tenant_id: int
    template_id: UUID4


class EmailSchedulerUpdate(BaseModel):
    trigger_type: Optional[str] = Field(None, max_length=20)
    trigger_event: Optional[str] = Field(None, max_length=50)
    cron_expression: Optional[str] = Field(None, max_length=50)
    recipient_type: Optional[str] = Field(None, max_length=30)
    recipient_filter: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    next_run_at: Optional[datetime] = None


class EmailSchedulerResponse(EmailSchedulerBase):
    scheduler_id: UUID4
    tenant_id: int
    template_id: UUID4
    last_run_at: Optional[datetime]
    next_run_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ─── WhatsApp Scheduler Schemas ──────────────────────────────────────────────

class WASchedulerBase(BaseModel):
    trigger_type: str = Field(..., max_length=20)
    trigger_event: Optional[str] = Field(None, max_length=50)
    cron_expression: Optional[str] = Field(None, max_length=50)
    recipient_type: str = Field(..., max_length=30)
    recipient_filter: Optional[Dict[str, Any]] = None
    is_active: bool = True


class WASchedulerCreate(WASchedulerBase):
    tenant_id: int
    wa_template_id: UUID4


class WASchedulerUpdate(BaseModel):
    trigger_type: Optional[str] = Field(None, max_length=20)
    trigger_event: Optional[str] = Field(None, max_length=50)
    cron_expression: Optional[str] = Field(None, max_length=50)
    recipient_type: Optional[str] = Field(None, max_length=30)
    recipient_filter: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    next_run_at: Optional[datetime] = None


class WASchedulerResponse(WASchedulerBase):
    scheduler_id: UUID4
    tenant_id: int
    wa_template_id: UUID4
    last_run_at: Optional[datetime]
    next_run_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
