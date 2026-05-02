from pydantic import BaseModel
from typing import Optional, List, Any, Dict
from datetime import datetime, date


class SubscriptionPlanOut(BaseModel):
    subscription_id:    int
    plan_name:          str
    plan_code:          str
    description:        Optional[str]
    price_monthly:      float
    price_yearly:       float
    max_users:          int
    max_clients:        Optional[int]
    max_branches:       int
    storage_limit_gb:   Optional[float]
    features_json:      Optional[Dict[str, Any]]
    trial_days:         int
    is_active:          bool
    sort_order:         int
    model_config = {"from_attributes": True}


class CurrentSubscriptionOut(BaseModel):
    # Subscription plan info
    subscription_id:    int
    plan_name:          str
    plan_code:          str
    price_monthly:      float
    price_yearly:       float
    max_users:          int
    max_clients:        Optional[int]
    max_branches:       int
    features_json:      Optional[Dict[str, Any]]

    # Current period info (from SubscriptionHistory)
    history_id:         int
    billing_cycle:      str
    start_date:         date
    end_date:           date
    amount_paid:        Optional[float]
    action:             str

    # Tenant status
    tenant_status:      str
    trial_end_date:     Optional[date]
    is_trial:           bool
    days_remaining:     int

    # Usage
    current_user_count:     int
    current_client_count:   int
    current_branch_count:   int

    # Stripe
    stripe_customer_id:     Optional[str] = None
    stripe_subscription_id: Optional[str] = None

    model_config = {"from_attributes": True}


class CheckoutSessionRequest(BaseModel):
    plan_code:      str        # BASIC, PRO, ENT
    billing_cycle:  str = "MONTHLY"   # MONTHLY or YEARLY


class CheckoutSessionOut(BaseModel):
    session_id:     str
    checkout_url:   str
    publishable_key: str


class PortalSessionOut(BaseModel):
    portal_url: str


class UpgradePreviewOut(BaseModel):
    current_plan:       str
    new_plan:           str
    billing_cycle:      str
    current_price:      float
    new_price:          float
    price_difference:   float
    is_upgrade:         bool
    effective_date:     str
    proration_note:     str


class WebhookResponse(BaseModel):
    received: bool


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
