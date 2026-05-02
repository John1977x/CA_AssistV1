from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.deps import get_db, get_current_user
from app.models.auth import User
from app.models.company import TenantCompany, CustomerCompany, ClientDocument
from app.schemas.company import (
    TenantCompanyCreate, TenantCompanyUpdate, TenantCompanyResponse,
    CustomerCompanyCreate, CustomerCompanyUpdate, CustomerCompanyResponse,
    ClientDocumentCreate, ClientDocumentUpdate, ClientDocumentResponse
)

router = APIRouter()


# ─── Tenant Companies ────────────────────────────────────────────────────────

@router.get("/tenant-companies", response_model=List[TenantCompanyResponse])
def list_tenant_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all tenant companies"""
    companies = db.query(TenantCompany).filter(
        TenantCompany.tenant_id == current_user.tenant_id
    ).offset(skip).limit(limit).all()
    return companies


@router.post("/tenant-companies", response_model=TenantCompanyResponse, status_code=status.HTTP_201_CREATED)
def create_tenant_company(
    company_in: TenantCompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new tenant company"""
    # Check if company code already exists
    existing = db.query(TenantCompany).filter(
        TenantCompany.company_code == company_in.company_code
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company code already exists"
        )
    
    company = TenantCompany(**company_in.dict())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@router.get("/tenant-companies/{company_id}", response_model=TenantCompanyResponse)
def get_tenant_company(
    company_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific tenant company"""
    company = db.query(TenantCompany).filter(
        TenantCompany.company_id == company_id,
        TenantCompany.tenant_id == current_user.tenant_id
    ).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.put("/tenant-companies/{company_id}", response_model=TenantCompanyResponse)
def update_tenant_company(
    company_id: UUID,
    company_in: TenantCompanyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a tenant company"""
    company = db.query(TenantCompany).filter(
        TenantCompany.company_id == company_id,
        TenantCompany.tenant_id == current_user.tenant_id
    ).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    for field, value in company_in.dict(exclude_unset=True).items():
        setattr(company, field, value)
    
    db.commit()
    db.refresh(company)
    return company


@router.delete("/tenant-companies/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tenant_company(
    company_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a tenant company"""
    company = db.query(TenantCompany).filter(
        TenantCompany.company_id == company_id,
        TenantCompany.tenant_id == current_user.tenant_id
    ).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    db.delete(company)
    db.commit()
    return None


# ─── Customer Companies ──────────────────────────────────────────────────────

@router.get("/customer-companies", response_model=List[CustomerCompanyResponse])
def list_customer_companies(
    customer_id: int = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List customer companies"""
    query = db.query(CustomerCompany).filter(
        CustomerCompany.tenant_id == current_user.tenant_id
    )
    if customer_id:
        query = query.filter(CustomerCompany.customer_id == customer_id)
    
    companies = query.offset(skip).limit(limit).all()
    return companies


@router.post("/customer-companies", response_model=CustomerCompanyResponse, status_code=status.HTTP_201_CREATED)
def create_customer_company(
    company_in: CustomerCompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new customer company"""
    # Check if company code already exists
    existing = db.query(CustomerCompany).filter(
        CustomerCompany.company_code == company_in.company_code
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company code already exists"
        )
    
    company = CustomerCompany(**company_in.dict())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@router.get("/customer-companies/{company_id}", response_model=CustomerCompanyResponse)
def get_customer_company(
    company_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific customer company"""
    company = db.query(CustomerCompany).filter(
        CustomerCompany.company_id == company_id,
        CustomerCompany.tenant_id == current_user.tenant_id
    ).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.put("/customer-companies/{company_id}", response_model=CustomerCompanyResponse)
def update_customer_company(
    company_id: UUID,
    company_in: CustomerCompanyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a customer company"""
    company = db.query(CustomerCompany).filter(
        CustomerCompany.company_id == company_id,
        CustomerCompany.tenant_id == current_user.tenant_id
    ).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    for field, value in company_in.dict(exclude_unset=True).items():
        setattr(company, field, value)
    
    db.commit()
    db.refresh(company)
    return company


@router.delete("/customer-companies/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer_company(
    company_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a customer company"""
    company = db.query(CustomerCompany).filter(
        CustomerCompany.company_id == company_id,
        CustomerCompany.tenant_id == current_user.tenant_id
    ).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    db.delete(company)
    db.commit()
    return None


# ─── Client Documents ────────────────────────────────────────────────────────

@router.get("/documents", response_model=List[ClientDocumentResponse])
def list_documents(
    customer_id: int = Query(None),
    company_id: UUID = Query(None),
    document_type: str = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List client documents"""
    query = db.query(ClientDocument).filter(
        ClientDocument.tenant_id == current_user.tenant_id
    )
    if customer_id:
        query = query.filter(ClientDocument.customer_id == customer_id)
    if company_id:
        query = query.filter(ClientDocument.company_id == company_id)
    if document_type:
        query = query.filter(ClientDocument.document_type == document_type)
    
    documents = query.offset(skip).limit(limit).all()
    return documents


@router.post("/documents", response_model=ClientDocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(
    document_in: ClientDocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new client document"""
    document = ClientDocument(**document_in.dict())
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


@router.get("/documents/{document_id}", response_model=ClientDocumentResponse)
def get_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific document"""
    document = db.query(ClientDocument).filter(
        ClientDocument.client_doc_id == document_id,
        ClientDocument.tenant_id == current_user.tenant_id
    ).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.put("/documents/{document_id}", response_model=ClientDocumentResponse)
def update_document(
    document_id: UUID,
    document_in: ClientDocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a document"""
    document = db.query(ClientDocument).filter(
        ClientDocument.client_doc_id == document_id,
        ClientDocument.tenant_id == current_user.tenant_id
    ).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    update_data = document_in.dict(exclude_unset=True)
    if 'verified_by' in update_data and update_data['verified_by']:
        from datetime import datetime
        document.verified_at = datetime.now()
    
    for field, value in update_data.items():
        setattr(document, field, value)
    
    db.commit()
    db.refresh(document)
    return document


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a document"""
    document = db.query(ClientDocument).filter(
        ClientDocument.client_doc_id == document_id,
        ClientDocument.tenant_id == current_user.tenant_id
    ).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    db.delete(document)
    db.commit()
    return None
