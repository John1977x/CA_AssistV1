from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class TicketCommentCreate(BaseModel):
    comment_text: str
    is_internal: bool = False


class TicketCommentOut(BaseModel):
    comment_id: int
    ticket_id: int
    user_id: int
    comment_text: str
    is_internal: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TicketCreate(BaseModel):
    title: str
    description: str
    category: str  # TECHNICAL, BILLING, GENERAL, URGENT
    priority: Optional[str] = "MEDIUM"
    tags: Optional[List[str]] = None


class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    assigned_to_user_id: Optional[int] = None
    resolution: Optional[str] = None
    tags: Optional[List[str]] = None


class TicketOut(BaseModel):
    ticket_id: int
    ticket_number: str
    title: str
    description: str
    category: str
    priority: str
    status: str
    resolution: Optional[str]
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime]
    closed_at: Optional[datetime]
    assigned_to_user_id: Optional[int]
    raised_by_user_id: int
    resolved_by_user_id: Optional[int]

    class Config:
        from_attributes = True


class TicketDetailOut(TicketOut):
    comments: List[TicketCommentOut] = []


class PaginatedResponse(BaseModel):
    items: List
    total: int
    page: int
    page_size: int
    total_pages: int


class CloseTicketRequest(BaseModel):
    resolution: str


class MessageResponse(BaseModel):
    message: str
