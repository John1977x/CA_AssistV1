from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import math

from app.db.session import get_db
from app.core.deps import get_current_active_user
from app.models.auth import User
from app.schemas.customer import (
    EnquiryCreate, EnquiryUpdate, EnquiryOut, EnquiryListOut,
    EnquiryConvertRequest, PaginatedResponse, MessageResponse, CustomerOut,
)
from app.services import enquiry as svc

router = APIRouter(prefix="/enquiries", tags=["Enquiries"])


@router.get("/stats")
async def enquiry_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return await svc.get_enquiry_stats(db, current_user.tenant_id)


@router.get("", response_model=PaginatedResponse)
async def list_enquiries(
    page:               int           = Query(1, ge=1),
    page_size:          int           = Query(20, ge=1, le=100),
    search:             Optional[str] = Query(None),
    status:             Optional[str] = Query(None),
    source:             Optional[str] = Query(None),
    assigned_to_user_id: Optional[int]= Query(None),
    is_converted:       Optional[bool]= Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    enquiries, total = await svc.get_enquiries(
        db, current_user.tenant_id, page, page_size,
        search, status, source, assigned_to_user_id, is_converted,
    )
    return PaginatedResponse(
        items=[EnquiryListOut.model_validate(e) for e in enquiries],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total else 1,
    )


@router.post("", response_model=EnquiryOut, status_code=201)
async def create_enquiry(
    data: EnquiryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    enquiry = await svc.create_enquiry(db, current_user.tenant_id, data)
    return EnquiryOut.model_validate(enquiry)


@router.get("/{enquiry_id}", response_model=EnquiryOut)
async def get_enquiry(
    enquiry_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    enquiry = await svc.get_enquiry(db, current_user.tenant_id, enquiry_id)
    return EnquiryOut.model_validate(enquiry)


@router.patch("/{enquiry_id}", response_model=EnquiryOut)
async def update_enquiry(
    data: EnquiryUpdate,
    enquiry_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    enquiry = await svc.update_enquiry(db, current_user.tenant_id, enquiry_id, data)
    return EnquiryOut.model_validate(enquiry)


@router.delete("/{enquiry_id}", response_model=MessageResponse)
async def delete_enquiry(
    enquiry_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    await svc.delete_enquiry(db, current_user.tenant_id, enquiry_id)
    return MessageResponse(message="Enquiry closed.")


@router.post("/{enquiry_id}/convert", response_model=CustomerOut)
async def convert_to_customer(
    data: EnquiryConvertRequest,
    enquiry_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Convert an enquiry into a full customer record."""
    customer = await svc.convert_enquiry(
        db, current_user.tenant_id, enquiry_id, data, current_user.user_id
    )
    return CustomerOut.model_validate(customer)
