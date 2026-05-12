from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


DOC_TYPES = [
    "LETTER", "NOTICE", "CERTIFICATE", "FORM",
    "APPLICATION", "CONTRACT", "REPORT", "INVOICE", "OTHER",
]


class RegisterCreate(BaseModel):
    in_out_ward: str = Field(..., pattern="^(INWARD|OUTWARD)$")
    doc_date: date
    doc_type: str = Field(..., max_length=60)
    doc_description: str = Field(..., min_length=2)
    client_id: Optional[int] = None
    owner_id: Optional[int] = None
    employee_id: Optional[int] = None
    sent_date: Optional[date] = None
    acknowledgement: Optional[str] = Field(None, max_length=200)


class RegisterUpdate(BaseModel):
    in_out_ward: Optional[str] = Field(None, pattern="^(INWARD|OUTWARD)$")
    doc_date: Optional[date] = None
    doc_type: Optional[str] = Field(None, max_length=60)
    doc_description: Optional[str] = None
    client_id: Optional[int] = None
    owner_id: Optional[int] = None
    employee_id: Optional[int] = None
    sent_date: Optional[date] = None
    acknowledgement: Optional[str] = Field(None, max_length=200)


class RegisterOut(BaseModel):
    register_id: int
    tenant_id: int
    in_out_ward: str
    doc_date: date
    doc_type: str
    doc_description: str
    client_id: Optional[int]
    owner_id: Optional[int]
    employee_id: Optional[int]
    sent_date: Optional[date]
    acknowledgement: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaginatedRegisters(BaseModel):
    items: List[RegisterOut]
    total: int
    page: int
    page_size: int
    total_pages: int


class RegisterStats(BaseModel):
    total: int
    inward: int
    outward: int
    pending_ack: int
