from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Any, Dict
from datetime import datetime, date
import re


# ─── Customer Schemas ────────────────────────────────────────────────────────

CUSTOMER_TYPES = ["INDIVIDUAL", "COMPANY", "HUF", "TRUST", "LLP", "PARTNERSHIP", "AOP", "BOI"]
CUSTOMER_STATUSES = ["ACTIVE", "INACTIVE", "PROSPECT", "CHURNED"]
KYC_STATUSES = ["PENDING", "VERIFIED", "EXPIRED", "REJECTED"]
RISK_LEVELS = ["LOW", "MEDIUM", "HIGH"]
SOURCE_CHANNELS = ["WALK_IN", "WEBSITE", "REFERRAL", "SOCIAL_MEDIA", "ADVERTISEMENT", "OTHER"]


class CustomerCreate(BaseModel):
    customer_type:      str = Field("INDIVIDUAL")
    display_name:       str = Field(..., min_length=2, max_length=200)
    legal_name:         Optional[str] = None
    pan:                Optional[str] = None
    gstin:              Optional[str] = None
    aadhar_number:      Optional[str] = None
    email:              Optional[str] = None
    phone:              str = Field(..., min_length=10, max_length=15)
    alternate_phone:    Optional[str] = None
    whatsapp:           Optional[str] = None
    date_of_birth:      Optional[date] = None
    date_of_incorporation: Optional[date] = None
    industry_code:      Optional[str] = None
    source_channel:     Optional[str] = None
    referred_by_customer_id: Optional[int] = None
    tags:               Optional[List[str]] = None
    notes:              Optional[str] = None
    branch_id:          Optional[int] = None
    assigned_user_id:   Optional[int] = None
    onboarded_at:       Optional[date] = None

    @field_validator("legal_name", "pan", "gstin", "aadhar_number", "email", "alternate_phone", "whatsapp", "industry_code", "source_channel", "notes", mode="before")
    @classmethod
    def empty_str_to_none(cls, v):
        """Convert empty strings to None for optional fields"""
        if isinstance(v, str) and v.strip() == "":
            return None
        return v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        """Validate email format if provided"""
        if v and "@" not in v:
            raise ValueError("Invalid email format")
        return v

    @field_validator("pan")
    @classmethod
    def validate_pan(cls, v):
        if v and not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', v.upper()):
            raise ValueError("Invalid PAN format (e.g. ABCDE1234F)")
        return v.upper() if v else v

    @field_validator("gstin")
    @classmethod
    def validate_gstin(cls, v):
        # Accept any 15-character value as GSTIN (validation is lenient)
        if v and len(v) != 15:
            raise ValueError("GSTIN must be exactly 15 characters")
        return v.upper() if v else v


class CustomerUpdate(BaseModel):
    customer_type:      Optional[str] = None
    display_name:       Optional[str] = Field(None, min_length=2, max_length=200)
    legal_name:         Optional[str] = None
    pan:                Optional[str] = None
    gstin:              Optional[str] = None
    email:              Optional[str] = None
    phone:              Optional[str] = None
    alternate_phone:    Optional[str] = None
    whatsapp:           Optional[str] = None
    date_of_birth:      Optional[date] = None
    date_of_incorporation: Optional[date] = None
    industry_code:      Optional[str] = None
    source_channel:     Optional[str] = None
    tags:               Optional[List[str]] = None
    notes:              Optional[str] = None
    branch_id:          Optional[int] = None
    assigned_user_id:   Optional[int] = None
    status:             Optional[str] = None
    risk_level:         Optional[str] = None
    kyc_status:         Optional[str] = None
    portal_access:      Optional[bool] = None
    portal_email:       Optional[str] = None

    @field_validator("*", mode="before")
    @classmethod
    def empty_str_to_none(cls, v):
        """Convert empty strings to None for optional fields"""
        if isinstance(v, str) and v.strip() == "":
            return None
        return v

    @field_validator("email", "portal_email")
    @classmethod
    def validate_email(cls, v):
        """Validate email format if provided"""
        if v and "@" not in v:
            raise ValueError("Invalid email format")
        return v

    @field_validator("pan")
    @classmethod
    def validate_pan(cls, v):
        if v and not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', v.upper()):
            raise ValueError("Invalid PAN format (e.g. ABCDE1234F)")
        return v.upper() if v else v

    @field_validator("gstin")
    @classmethod
    def validate_gstin(cls, v):
        # Accept any 15-character value as GSTIN (validation is lenient)
        if v and len(v) != 15:
            raise ValueError("GSTIN must be exactly 15 characters")
        return v.upper() if v else v


class CustomerDetailsCreate(BaseModel):
    registered_address_line1:   Optional[str] = None
    registered_address_line2:   Optional[str] = None
    registered_city:            Optional[str] = None
    registered_state:           Optional[str] = None
    registered_pincode:         Optional[str] = None
    communication_address:      Optional[str] = None
    bank_name:                  Optional[str] = None
    bank_account_number:        Optional[str] = None
    bank_ifsc:                  Optional[str] = None
    bank_account_type:          Optional[str] = None
    income_tax_status:          Optional[str] = None
    gst_registration_type:      Optional[str] = None
    gst_registration_date:      Optional[date] = None
    gst_cancellation_date:      Optional[date] = None
    tds_deductor_type:          Optional[str] = None
    director_partners_json:     Optional[List[Dict[str, Any]]] = None
    custom_fields_json:         Optional[Dict[str, Any]] = None


class CustomerDetailsOut(BaseModel):
    customer_detail_id:         int
    customer_id:                int
    registered_address_line1:   Optional[str]
    registered_address_line2:   Optional[str]
    registered_city:            Optional[str]
    registered_state:           Optional[str]
    registered_pincode:         Optional[str]
    communication_address:      Optional[str]
    bank_name:                  Optional[str]
    bank_account_number:        Optional[str]
    bank_ifsc:                  Optional[str]
    bank_account_type:          Optional[str]
    income_tax_status:          Optional[str]
    gst_registration_type:      Optional[str]
    gst_registration_date:      Optional[date]
    gst_cancellation_date:      Optional[date]
    tds_deductor_type:          Optional[str]
    director_partners_json:     Optional[List[Dict[str, Any]]]
    custom_fields_json:         Optional[Dict[str, Any]]
    updated_at:                 datetime

    model_config = {"from_attributes": True}


class AssignedUserBrief(BaseModel):
    user_id:        int
    display_name:   Optional[str]
    email:          str
    model_config = {"from_attributes": True}


class CustomerOut(BaseModel):
    customer_id:            int
    tenant_id:              int
    customer_code:          str
    customer_type:          str
    display_name:           str
    legal_name:             Optional[str]
    pan:                    Optional[str]
    gstin:                  Optional[str]
    aadhar_number:          Optional[str]
    email:                  Optional[str]
    phone:                  str
    alternate_phone:        Optional[str]
    whatsapp:               Optional[str]
    date_of_birth:          Optional[date]
    date_of_incorporation:  Optional[date]
    industry_code:          Optional[str]
    source_channel:         Optional[str]
    tags:                   Optional[List[str]]
    portal_access:          bool
    portal_email:           Optional[str]
    status:                 str
    risk_level:             Optional[str]
    kyc_status:             str
    kyc_verified_at:        Optional[datetime]
    onboarded_at:           Optional[date]
    notes:                  Optional[str]
    branch_id:              Optional[int]
    assigned_user_id:       Optional[int]
    referred_by_customer_id: Optional[int]
    created_at:             datetime
    updated_at:             datetime

    model_config = {"from_attributes": True}


class CustomerListOut(BaseModel):
    customer_id:    int
    customer_code:  str
    customer_type:  str
    display_name:   str
    pan:            Optional[str]
    gstin:          Optional[str]
    aadhar_number:  Optional[str]
    email:          Optional[str]
    phone:          str
    status:         str
    kyc_status:     str
    risk_level:     Optional[str]
    tags:           Optional[List[str]]
    onboarded_at:   Optional[date]
    assigned_user_id: Optional[int]
    created_at:     datetime

    model_config = {"from_attributes": True}


# ─── Enquiry Schemas ─────────────────────────────────────────────────────────

ENQUIRY_STATUSES = ["NEW", "IN_PROGRESS", "PROPOSAL_SENT", "WON", "LOST", "DEFERRED"]
SERVICES_LIST = ["GST", "ITR", "TDS", "Audit", "ROC", "Accounting", "Payroll", "Investment Advisory", "Other"]


class EnquiryCreate(BaseModel):
    full_name:              str = Field(..., min_length=2, max_length=200)
    email:                  Optional[str] = None
    phone:                  str = Field(..., min_length=10, max_length=15)
    company_name:           Optional[str] = None
    service_interested:     Optional[List[str]] = None
    source:                 Optional[str] = None
    referred_by_customer_id: Optional[int] = None
    message:                Optional[str] = None
    estimated_value:        Optional[float] = None
    branch_id:              Optional[int] = None
    assigned_to_user_id:    Optional[int] = None
    follow_up_date:         Optional[date] = None
    enquiry_date:           Optional[date] = None

    @field_validator("*", mode="before")
    @classmethod
    def empty_str_to_none(cls, v):
        """Convert empty strings to None for optional fields"""
        if isinstance(v, str) and v.strip() == "":
            return None
        return v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        """Validate email format if provided"""
        if v and "@" not in v:
            raise ValueError("Invalid email format")
        return v


class EnquiryUpdate(BaseModel):
    full_name:              Optional[str] = None
    email:                  Optional[str] = None
    phone:                  Optional[str] = None
    company_name:           Optional[str] = None
    service_interested:     Optional[List[str]] = None
    source:                 Optional[str] = None
    message:                Optional[str] = None
    estimated_value:        Optional[float] = None
    status:                 Optional[str] = None
    follow_up_date:         Optional[date] = None
    follow_up_notes:        Optional[str] = None
    lost_reason:            Optional[str] = None
    assigned_to_user_id:    Optional[int] = None

    @field_validator("*", mode="before")
    @classmethod
    def empty_str_to_none(cls, v):
        """Convert empty strings to None for optional fields"""
        if isinstance(v, str) and v.strip() == "":
            return None
        return v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        """Validate email format if provided"""
        if v and "@" not in v:
            raise ValueError("Invalid email format")
        return v


class EnquiryConvertRequest(BaseModel):
    """Convert an enquiry to a full customer record."""
    customer_type:  str = "INDIVIDUAL"
    display_name:   Optional[str] = None
    pan:            Optional[str] = None
    gstin:          Optional[str] = None
    onboarded_at:   Optional[date] = None
    assigned_user_id: Optional[int] = None
    branch_id:      Optional[int] = None


class EnquiryOut(BaseModel):
    enquiry_id:             int
    tenant_id:              int
    enquiry_number:         str
    enquiry_date:           date
    full_name:              str
    email:                  Optional[str]
    phone:                  str
    company_name:           Optional[str]
    service_interested:     Optional[List[str]]
    source:                 Optional[str]
    message:                Optional[str]
    estimated_value:        Optional[float]
    status:                 str
    follow_up_date:         Optional[date]
    follow_up_notes:        Optional[str]
    lost_reason:            Optional[str]
    is_converted:           bool
    converted_customer_id:  Optional[int]
    converted_at:           Optional[datetime]
    branch_id:              Optional[int]
    assigned_to_user_id:    Optional[int]
    referred_by_customer_id: Optional[int]
    created_at:             datetime
    updated_at:             datetime

    model_config = {"from_attributes": True}


class EnquiryListOut(BaseModel):
    enquiry_id:         int
    enquiry_number:     str
    enquiry_date:       date
    full_name:          str
    phone:              str
    email:              Optional[str]
    company_name:       Optional[str]
    service_interested: Optional[List[str]]
    source:             Optional[str]
    estimated_value:    Optional[float]
    status:             str
    follow_up_date:     Optional[date]
    is_converted:       bool
    assigned_to_user_id: Optional[int]
    created_at:         datetime

    model_config = {"from_attributes": True}


# ─── Shared ──────────────────────────────────────────────────────────────────

class PaginatedResponse(BaseModel):
    items:          List[Any]
    total:          int
    page:           int
    page_size:      int
    total_pages:    int


class MessageResponse(BaseModel):
    message:    str
    success:    bool = True
    data:       Optional[Any] = None
