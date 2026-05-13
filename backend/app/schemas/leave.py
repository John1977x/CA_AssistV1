from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


LEAVE_TYPES = ["Annual", "Sick", "Casual", "Maternity", "Paternity", "Emergency", "Unpaid", "Compensatory", "Other"]
CALCULATIONS = ["MONTHLY", "YEARLY", "QUARTERLY"]


class LeaveMasterCreate(BaseModel):
    leave_type:    str = Field(..., min_length=1, max_length=100)
    entitled:      int = Field(..., ge=0)
    calendar_year: int = Field(..., ge=2000, le=2100)
    calculation:   str = Field(..., min_length=1, max_length=50)


class LeaveMasterUpdate(BaseModel):
    leave_type:    Optional[str] = Field(None, min_length=1, max_length=100)
    entitled:      Optional[int] = Field(None, ge=0)
    calendar_year: Optional[int] = Field(None, ge=2000, le=2100)
    calculation:   Optional[str] = Field(None, min_length=1, max_length=50)


class LeaveMasterOut(BaseModel):
    leave_master_id: int
    tenant_id:       int
    leave_type:      str
    entitled:        int
    calendar_year:   int
    calculation:     str
    created_at:      datetime
    updated_at:      datetime

    model_config = {"from_attributes": True}


class PaginatedLeaveMasters(BaseModel):
    items:       List[LeaveMasterOut]
    total:       int
    page:        int
    page_size:   int
    total_pages: int
