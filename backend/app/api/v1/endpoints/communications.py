from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.deps import get_db, get_current_user
from app.models.auth import User
from app.models.communication import (
    EmailTemplate, EmailQueue, WATemplate, WAQueue,
    EmailScheduler, WAScheduler
)
from app.schemas.communication import (
    EmailTemplateCreate, EmailTemplateUpdate, EmailTemplateResponse,
    EmailQueueCreate, EmailQueueUpdate, EmailQueueResponse,
    WATemplateCreate, WATemplateUpdate, WATemplateResponse,
    WAQueueCreate, WAQueueUpdate, WAQueueResponse,
    EmailSchedulerCreate, EmailSchedulerUpdate, EmailSchedulerResponse,
    WASchedulerCreate, WASchedulerUpdate, WASchedulerResponse
)

router = APIRouter()


# ─── Email Templates ─────────────────────────────────────────────────────────

@router.get("/email-templates", response_model=List[EmailTemplateResponse])
def list_email_templates(
    category: str = Query(None),
    is_active: bool = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List email templates"""
    query = db.query(EmailTemplate).filter(
        EmailTemplate.tenant_id == current_user.tenant_id
    )
    if category:
        query = query.filter(EmailTemplate.category == category)
    if is_active is not None:
        query = query.filter(EmailTemplate.is_active == is_active)
    
    templates = query.offset(skip).limit(limit).all()
    return templates


@router.post("/email-templates", response_model=EmailTemplateResponse, status_code=status.HTTP_201_CREATED)
def create_email_template(
    template_in: EmailTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new email template"""
    # Check if template code already exists
    existing = db.query(EmailTemplate).filter(
        EmailTemplate.template_code == template_in.template_code
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Template code already exists"
        )
    
    template = EmailTemplate(**template_in.dict())
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@router.get("/email-templates/{template_id}", response_model=EmailTemplateResponse)
def get_email_template(
    template_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific email template"""
    template = db.query(EmailTemplate).filter(
        EmailTemplate.template_id == template_id,
        EmailTemplate.tenant_id == current_user.tenant_id
    ).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.put("/email-templates/{template_id}", response_model=EmailTemplateResponse)
def update_email_template(
    template_id: UUID,
    template_in: EmailTemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an email template"""
    template = db.query(EmailTemplate).filter(
        EmailTemplate.template_id == template_id,
        EmailTemplate.tenant_id == current_user.tenant_id
    ).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    for field, value in template_in.dict(exclude_unset=True).items():
        setattr(template, field, value)
    
    db.commit()
    db.refresh(template)
    return template


@router.delete("/email-templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_email_template(
    template_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an email template"""
    template = db.query(EmailTemplate).filter(
        EmailTemplate.template_id == template_id,
        EmailTemplate.tenant_id == current_user.tenant_id
    ).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    db.delete(template)
    db.commit()
    return None


# ─── Email Queue ─────────────────────────────────────────────────────────────

@router.get("/email-queue", response_model=List[EmailQueueResponse])
def list_email_queue(
    status_filter: str = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List email queue"""
    query = db.query(EmailQueue).filter(
        EmailQueue.tenant_id == current_user.tenant_id
    )
    if status_filter:
        query = query.filter(EmailQueue.status == status_filter)
    
    emails = query.order_by(EmailQueue.created_at.desc()).offset(skip).limit(limit).all()
    return emails


@router.post("/email-queue", response_model=EmailQueueResponse, status_code=status.HTTP_201_CREATED)
def create_email_queue(
    email_in: EmailQueueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add email to queue"""
    email = EmailQueue(**email_in.dict())
    db.add(email)
    db.commit()
    db.refresh(email)
    return email


@router.get("/email-queue/{queue_id}", response_model=EmailQueueResponse)
def get_email_queue(
    queue_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific queued email"""
    email = db.query(EmailQueue).filter(
        EmailQueue.queue_id == queue_id,
        EmailQueue.tenant_id == current_user.tenant_id
    ).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    return email


@router.put("/email-queue/{queue_id}", response_model=EmailQueueResponse)
def update_email_queue(
    queue_id: UUID,
    email_in: EmailQueueUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update queued email"""
    email = db.query(EmailQueue).filter(
        EmailQueue.queue_id == queue_id,
        EmailQueue.tenant_id == current_user.tenant_id
    ).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    
    for field, value in email_in.dict(exclude_unset=True).items():
        setattr(email, field, value)
    
    db.commit()
    db.refresh(email)
    return email


# ─── WhatsApp Templates ──────────────────────────────────────────────────────

@router.get("/whatsapp-templates", response_model=List[WATemplateResponse])
def list_whatsapp_templates(
    category: str = Query(None),
    status_filter: str = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List WhatsApp templates"""
    query = db.query(WATemplate).filter(
        WATemplate.tenant_id == current_user.tenant_id
    )
    if category:
        query = query.filter(WATemplate.category == category)
    if status_filter:
        query = query.filter(WATemplate.status == status_filter)
    
    templates = query.offset(skip).limit(limit).all()
    return templates


@router.post("/whatsapp-templates", response_model=WATemplateResponse, status_code=status.HTTP_201_CREATED)
def create_whatsapp_template(
    template_in: WATemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new WhatsApp template"""
    # Check if template code already exists
    existing = db.query(WATemplate).filter(
        WATemplate.template_code == template_in.template_code
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Template code already exists"
        )
    
    template = WATemplate(**template_in.dict())
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@router.get("/whatsapp-templates/{template_id}", response_model=WATemplateResponse)
def get_whatsapp_template(
    template_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific WhatsApp template"""
    template = db.query(WATemplate).filter(
        WATemplate.wa_template_id == template_id,
        WATemplate.tenant_id == current_user.tenant_id
    ).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.put("/whatsapp-templates/{template_id}", response_model=WATemplateResponse)
def update_whatsapp_template(
    template_id: UUID,
    template_in: WATemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a WhatsApp template"""
    template = db.query(WATemplate).filter(
        WATemplate.wa_template_id == template_id,
        WATemplate.tenant_id == current_user.tenant_id
    ).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    for field, value in template_in.dict(exclude_unset=True).items():
        setattr(template, field, value)
    
    db.commit()
    db.refresh(template)
    return template


# ─── WhatsApp Queue ──────────────────────────────────────────────────────────

@router.get("/whatsapp-queue", response_model=List[WAQueueResponse])
def list_whatsapp_queue(
    status_filter: str = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List WhatsApp queue"""
    query = db.query(WAQueue).filter(
        WAQueue.tenant_id == current_user.tenant_id
    )
    if status_filter:
        query = query.filter(WAQueue.status == status_filter)
    
    messages = query.order_by(WAQueue.created_at.desc()).offset(skip).limit(limit).all()
    return messages


@router.post("/whatsapp-queue", response_model=WAQueueResponse, status_code=status.HTTP_201_CREATED)
def create_whatsapp_queue(
    message_in: WAQueueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add WhatsApp message to queue"""
    message = WAQueue(**message_in.dict())
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


@router.get("/whatsapp-queue/{queue_id}", response_model=WAQueueResponse)
def get_whatsapp_queue(
    queue_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific queued WhatsApp message"""
    message = db.query(WAQueue).filter(
        WAQueue.wa_queue_id == queue_id,
        WAQueue.tenant_id == current_user.tenant_id
    ).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message


@router.put("/whatsapp-queue/{queue_id}", response_model=WAQueueResponse)
def update_whatsapp_queue(
    queue_id: UUID,
    message_in: WAQueueUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update queued WhatsApp message"""
    message = db.query(WAQueue).filter(
        WAQueue.wa_queue_id == queue_id,
        WAQueue.tenant_id == current_user.tenant_id
    ).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    for field, value in message_in.dict(exclude_unset=True).items():
        setattr(message, field, value)
    
    db.commit()
    db.refresh(message)
    return message


# ─── Email Schedulers ────────────────────────────────────────────────────────

@router.get("/email-schedulers", response_model=List[EmailSchedulerResponse])
def list_email_schedulers(
    is_active: bool = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List email schedulers"""
    query = db.query(EmailScheduler).filter(
        EmailScheduler.tenant_id == current_user.tenant_id
    )
    if is_active is not None:
        query = query.filter(EmailScheduler.is_active == is_active)
    
    schedulers = query.all()
    return schedulers


@router.post("/email-schedulers", response_model=EmailSchedulerResponse, status_code=status.HTTP_201_CREATED)
def create_email_scheduler(
    scheduler_in: EmailSchedulerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new email scheduler"""
    scheduler = EmailScheduler(**scheduler_in.dict())
    db.add(scheduler)
    db.commit()
    db.refresh(scheduler)
    return scheduler


@router.put("/email-schedulers/{scheduler_id}", response_model=EmailSchedulerResponse)
def update_email_scheduler(
    scheduler_id: UUID,
    scheduler_in: EmailSchedulerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an email scheduler"""
    scheduler = db.query(EmailScheduler).filter(
        EmailScheduler.scheduler_id == scheduler_id,
        EmailScheduler.tenant_id == current_user.tenant_id
    ).first()
    if not scheduler:
        raise HTTPException(status_code=404, detail="Scheduler not found")
    
    for field, value in scheduler_in.dict(exclude_unset=True).items():
        setattr(scheduler, field, value)
    
    db.commit()
    db.refresh(scheduler)
    return scheduler


# ─── WhatsApp Schedulers ─────────────────────────────────────────────────────

@router.get("/whatsapp-schedulers", response_model=List[WASchedulerResponse])
def list_whatsapp_schedulers(
    is_active: bool = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List WhatsApp schedulers"""
    query = db.query(WAScheduler).filter(
        WAScheduler.tenant_id == current_user.tenant_id
    )
    if is_active is not None:
        query = query.filter(WAScheduler.is_active == is_active)
    
    schedulers = query.all()
    return schedulers


@router.post("/whatsapp-schedulers", response_model=WASchedulerResponse, status_code=status.HTTP_201_CREATED)
def create_whatsapp_scheduler(
    scheduler_in: WASchedulerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new WhatsApp scheduler"""
    scheduler = WAScheduler(**scheduler_in.dict())
    db.add(scheduler)
    db.commit()
    db.refresh(scheduler)
    return scheduler


@router.put("/whatsapp-schedulers/{scheduler_id}", response_model=WASchedulerResponse)
def update_whatsapp_scheduler(
    scheduler_id: UUID,
    scheduler_in: WASchedulerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a WhatsApp scheduler"""
    scheduler = db.query(WAScheduler).filter(
        WAScheduler.scheduler_id == scheduler_id,
        WAScheduler.tenant_id == current_user.tenant_id
    ).first()
    if not scheduler:
        raise HTTPException(status_code=404, detail="Scheduler not found")
    
    for field, value in scheduler_in.dict(exclude_unset=True).items():
        setattr(scheduler, field, value)
    
    db.commit()
    db.refresh(scheduler)
    return scheduler
