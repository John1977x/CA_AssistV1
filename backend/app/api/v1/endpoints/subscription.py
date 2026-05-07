from fastapi import APIRouter, Depends, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db.session import get_db
from app.core.deps import get_current_active_user, require_owner
from app.models.auth import User
from app.schemas.subscription import (
    SubscriptionPlanOut, CurrentSubscriptionOut,
    CheckoutSessionRequest, CheckoutSessionOut,
    PortalSessionOut, UpgradePreviewOut,
    WebhookResponse, MessageResponse,
)
from app.services import subscription as svc

router = APIRouter(prefix="/subscription", tags=["Subscription"])


# ─── Public: list all plans ───────────────────────────────────────────────────

@router.get("/plans", response_model=List[SubscriptionPlanOut])
async def list_plans(db: AsyncSession = Depends(get_db)):
    """Returns all available subscription plans. Public endpoint."""
    plans = await svc.get_all_plans(db)
    return [SubscriptionPlanOut.model_validate(p) for p in plans]


# ─── Current subscription ─────────────────────────────────────────────────────

@router.get("/current")
async def current_subscription(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get full current subscription status including usage and days remaining."""
    result = await svc.get_current_subscription(db, current_user.tenant_id)
    if result is None:
        return None
    return result


# ─── Preview upgrade/downgrade ────────────────────────────────────────────────

@router.get("/preview")
async def preview_change(
    plan_code: str,
    billing_cycle: str = "MONTHLY",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Preview price difference and proration before switching plans."""
    return await svc.preview_upgrade(db, current_user.tenant_id, plan_code, billing_cycle)


# ─── Stripe checkout ──────────────────────────────────────────────────────────

@router.post("/checkout", response_model=CheckoutSessionOut)
async def create_checkout(
    data: CheckoutSessionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_owner),
):
    """Create a Stripe Checkout session for plan purchase. Owner only."""
    return await svc.create_checkout_session(
        db, current_user.tenant_id,
        data.plan_code, data.billing_cycle,
        current_user.email,
    )


# ─── Stripe customer portal ───────────────────────────────────────────────────

@router.post("/portal", response_model=PortalSessionOut)
async def customer_portal(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_owner),
):
    """Get Stripe Customer Portal URL to manage billing, invoices, card details."""
    return await svc.create_portal_session(db, current_user.tenant_id)


# ─── Stripe webhook ───────────────────────────────────────────────────────────

@router.post("/webhook", response_model=WebhookResponse)
async def stripe_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """Stripe webhook endpoint. Register this URL in your Stripe dashboard."""
    payload = await request.body()
    return await svc.handle_stripe_webhook(db, payload, stripe_signature or "")
