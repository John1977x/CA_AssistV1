from pydantic import BaseModel, Field, UUID4
from typing import Optional
from datetime import date, datetime


# ─── Tenant Company Schemas ──────────────────────────────────────────────────

class TenantCompanyBase(BaseModel):
    company_code: str = Field(..., max_length=20)
    company_name: str = Field(..., max_length=200)
    phone: Optional[str] = Field(None, max_length=20)
    address1: Optional[str] = Field(None, max_length=200)
    address2: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    pincode: Optional[str] = Field(None, max_length=10)
    country: Optional[str] = Field(None, max_length=100)
    status: str = Field('Y', max_length=1)


class TenantCompanyCreate(TenantCompanyBase):
    tenant_id: int


class TenantCompanyUpdate(BaseModel):
    company_name: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=20)
    address1: Optional[str] = Field(None, max_length=200)
    address2: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    pincode: Optional[str] = Field(None, max_length=10)
    country: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field(None, max_length=1)


class TenantCompanyResponse(TenantCompanyBase):
    company_id: UUID4
    tenant_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Customer Company Schemas ────────────────────────────────────────────────

class CustomerCompanyBase(BaseModel):
    company_code: str = Field(..., max_length=20)
    company_name: str = Field(..., max_length=200)
    company_type: Optional[str] = Field(None, max_length=50)
    cin: Optional[str] = Field(None, max_length=21)
    pan: Optional[str] = Field(None, max_length=10)
    tan: Optional[str] = Field(None, max_length=10)
    gstin: Optional[str] = Field(None, max_length=15)
    incorporation_date: Optional[date] = None
    registered_address: Optional[str] = Field(None, max_length=300)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    pincode: Optional[str] = Field(None, max_length=10)
    country: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=150)
    is_primary: bool = False
    status: str = Field('Y', max_length=1)


class CustomerCompanyCreate(CustomerCompanyBase):
    customer_id: int
    tenant_id: int


class CustomerCompanyUpdate(BaseModel):
    company_name: Optional[str] = Field(None, max_length=200)
    company_type: Optional[str] = Field(None, max_length=50)
    cin: Optional[str] = Field(None, max_length=21)
    pan: Optional[str] = Field(None, max_length=10)
    tan: Optional[str] = Field(None, max_length=10)
    gstin: Optional[str] = Field(None, max_length=15)
    incorporation_date: Optional[date] = None
    registered_address: Optional[str] = Field(None, max_length=300)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    pincode: Optional[str] = Field(None, max_length=10)
    country: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=150)
    is_primary: Optional[bool] = None
    status: Optional[str] = Field(None, max_length=1)


class CustomerCompanyResponse(CustomerCompanyBase):
    company_id: UUID4
    customer_id: int
    tenant_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Client Document Schemas ─────────────────────────────────────────────────

class ClientDocumentBase(BaseModel):
    document_type: str = Field(..., max_length=50)
    document_number: Optional[str] = Field(None, max_length=50)
    document_name: str = Field(..., max_length=200)
    url: str = Field(..., max_length=500)
    size_kb: Optional[int] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    status: str = Field('Active', max_length=20)
    remarks: Optional[str] = Field(None, max_length=300)


class ClientDocumentCreate(ClientDocumentBase):
    customer_id: int
    company_id: Optional[UUID4] = None
    tenant_id: int


class ClientDocumentUpdate(BaseModel):
    document_type: Optional[str] = Field(None, max_length=50)
    document_number: Optional[str] = Field(None, max_length=50)
    document_name: Optional[str] = Field(None, max_length=200)
    url: Optional[str] = Field(None, max_length=500)
    size_kb: Optional[int] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    verified_by: Optional[int] = None
    status: Optional[str] = Field(None, max_length=20)
    remarks: Optional[str] = Field(None, max_length=300)


class ClientDocumentResponse(ClientDocumentBase):
    client_doc_id: UUID4
    customer_id: int
    company_id: Optional[UUID4]
    tenant_id: int
    verified_by: Optional[int]
    verified_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
