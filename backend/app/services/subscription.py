from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from fastapi import HTTPException
from datetime import datetime, timezone, date, timedelta
from typing import Optional
# import stripe  # TODO: Install stripe package

from app.models.auth import Tenant, User
from app.models.auth import Subscription, SubscriptionHistory
from app.core.config import settings

# Initialize Stripe
# stripe.api_key = settings.STRIPE_SECRET_KEY  # TODO: Uncomment when stripe is installed

# Stripe customer ID is stored in tenant notes_json for now
# In production you'd add stripe_customer_id column to Tenant


# ─── Plans ────────────────────────────────────────────────────────────────────

async def get_all_plans(db: AsyncSession):
    result = await db.execute(
        select(Subscription).where(Subscription.is_active == True)
        .order_by(Subscription.sort_order)
    )
    return result.scalars().all()


async def get_plan_by_code(db: AsyncSession, code: str) -> Subscription:
    result = await db.execute(
        select(Subscription).where(Subscription.plan_code == code, Subscription.is_active == True)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail=f"Plan '{code}' not found.")
    return plan


# ─── Current subscription ─────────────────────────────────────────────────────

async def get_current_subscription(db: AsyncSession, tenant_id: int) -> dict:
    # Get tenant
    tenant_r = await db.execute(select(Tenant).where(Tenant.tenant_id == tenant_id))
    tenant = tenant_r.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found.")

    # Get active subscription history
    hist_r = await db.execute(
        select(SubscriptionHistory).where(
            SubscriptionHistory.tenant_id == tenant_id,
            SubscriptionHistory.is_active == True,
        ).order_by(SubscriptionHistory.created_at.desc())
    )
    history = hist_r.scalar_one_or_none()
    if not history:
        raise HTTPException(status_code=404, detail="No active subscription found.")

    # Get plan
    plan_r = await db.execute(
        select(Subscription).where(Subscription.subscription_id == tenant.subscription_id)
    )
    plan = plan_r.scalar_one_or_none()

    # Usage counts
    from app.models.auth import User, Branch
    from app.models.customer import Customer

    user_count_r = await db.execute(
        select(func.count(User.user_id)).where(
            User.tenant_id == tenant_id,
            User.is_deleted == False,
            User.status.in_(["ACTIVE", "INVITED"]),
        )
    )
    client_count_r = await db.execute(
        select(func.count(Customer.customer_id)).where(
            Customer.tenant_id == tenant_id,
            Customer.is_deleted == False,
        )
    )
    branch_count_r = await db.execute(
        select(func.count(Branch.branch_id)).where(
            Branch.tenant_id == tenant_id,
            Branch.is_active == True,
        )
    )

    today = date.today()
    is_trial = tenant.status == "TRIAL"
    days_remaining = 0

    if is_trial and tenant.trial_end_date:
        days_remaining = max(0, (tenant.trial_end_date - today).days)
    elif history.end_date:
        days_remaining = max(0, (history.end_date - today).days)

    return {
        # Plan
        "subscription_id":      plan.subscription_id,
        "plan_name":            plan.plan_name,
        "plan_code":            plan.plan_code,
        "price_monthly":        float(plan.price_monthly),
        "price_yearly":         float(plan.price_yearly or 0),
        "max_users":            plan.max_users,
        "max_clients":          plan.max_clients,
        "max_branches":         plan.max_branches,
        "features_json":        plan.features_json or {},
        # History
        "history_id":           history.history_id,
        "billing_cycle":        history.billing_cycle,
        "start_date":           history.start_date,
        "end_date":             history.end_date,
        "amount_paid":          float(history.amount_paid or 0),
        "action":               history.action,
        # Tenant status
        "tenant_status":        tenant.status,
        "trial_end_date":       tenant.trial_end_date,
        "is_trial":             is_trial,
        "days_remaining":       days_remaining,
        # Usage
        "current_user_count":   user_count_r.scalar(),
        "current_client_count": client_count_r.scalar(),
        "current_branch_count": branch_count_r.scalar(),
    }


# ─── Stripe: Checkout session ─────────────────────────────────────────────────

async def create_checkout_session(
    db: AsyncSession, tenant_id: int, plan_code: str, billing_cycle: str, user_email: str
) -> dict:
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(status_code=503, detail="Stripe is not configured. Add STRIPE_SECRET_KEY to .env")

    plan = await get_plan_by_code(db, plan_code)
    price_map = settings.stripe_price_map
    price_id = price_map.get(plan_code, {}).get(billing_cycle.upper())

    if not price_id:
        raise HTTPException(
            status_code=400,
            detail=f"No Stripe price configured for {plan_code} {billing_cycle}. Add price IDs to .env"
        )

    # Get or create Stripe customer
    tenant_r = await db.execute(select(Tenant).where(Tenant.tenant_id == tenant_id))
    tenant = tenant_r.scalar_one_or_none()

    try:
        # Create Stripe checkout session
        session = stripe.checkout.Session.create(
            mode="subscription",
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            customer_email=user_email,
            success_url=f"{settings.FRONTEND_URL}/subscription/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.FRONTEND_URL}/subscription/plans",
            metadata={
                "tenant_id":    str(tenant_id),
                "plan_code":    plan_code,
                "billing_cycle": billing_cycle,
            },
            subscription_data={
                "metadata": {
                    "tenant_id": str(tenant_id),
                    "plan_code": plan_code,
                }
            },
            allow_promotion_codes=True,
        )
        return {
            "session_id":       session.id,
            "checkout_url":     session.url,
            "publishable_key":  settings.STRIPE_PUBLISHABLE_KEY,
        }
    except stripe.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ─── Stripe: Customer portal ──────────────────────────────────────────────────

async def create_portal_session(db: AsyncSession, tenant_id: int) -> dict:
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(status_code=503, detail="Stripe is not configured.")

    # In production, store stripe_customer_id on Tenant model
    # Here we look it up from Stripe by email
    tenant_r = await db.execute(select(Tenant).where(Tenant.tenant_id == tenant_id))
    tenant = tenant_r.scalar_one_or_none()

    try:
        customers = stripe.Customer.list(email=tenant.email, limit=1)
        if not customers.data:
            raise HTTPException(status_code=404, detail="No Stripe customer found. Please subscribe first.")

        session = stripe.billing_portal.Session.create(
            customer=customers.data[0].id,
            return_url=f"{settings.FRONTEND_URL}/subscription",
        )
        return {"portal_url": session.url}
    except stripe.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ─── Stripe: Upgrade preview ──────────────────────────────────────────────────

async def preview_upgrade(
    db: AsyncSession, tenant_id: int, new_plan_code: str, billing_cycle: str
) -> dict:
    current = await get_current_subscription(db, tenant_id)
    new_plan = await get_plan_by_code(db, new_plan_code)

    current_price = current["price_monthly"] if billing_cycle == "MONTHLY" else current["price_yearly"]
    new_price = float(new_plan.price_monthly) if billing_cycle == "MONTHLY" else float(new_plan.price_yearly or 0)
    diff = new_price - current_price

    is_upgrade = diff > 0
    action = "upgrade" if is_upgrade else "downgrade"

    return {
        "current_plan":     current["plan_name"],
        "new_plan":         new_plan.plan_name,
        "billing_cycle":    billing_cycle,
        "current_price":    current_price,
        "new_price":        new_price,
        "price_difference": diff,
        "is_upgrade":       is_upgrade,
        "effective_date":   date.today().isoformat(),
        "proration_note":   f"Your plan will {action} immediately. Stripe will prorate the charges on your next invoice." if is_upgrade
                           else f"Downgrade will take effect at the end of your current billing period."
    }


# ─── Stripe: Webhook handler ──────────────────────────────────────────────────

async def handle_stripe_webhook(db: AsyncSession, payload: bytes, sig_header: str):
    if not settings.STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=503, detail="Webhook secret not configured.")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except stripe.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid webhook signature.")

    event_type = event["type"]
    data = event["data"]["object"]

    if event_type == "checkout.session.completed":
        await _handle_checkout_completed(db, data)

    elif event_type == "customer.subscription.updated":
        await _handle_subscription_updated(db, data)

    elif event_type == "customer.subscription.deleted":
        await _handle_subscription_cancelled(db, data)

    elif event_type == "invoice.payment_failed":
        await _handle_payment_failed(db, data)

    return {"received": True}


async def _handle_checkout_completed(db: AsyncSession, session_data: dict):
    metadata = session_data.get("metadata", {})
    tenant_id = int(metadata.get("tenant_id", 0))
    plan_code = metadata.get("plan_code", "")
    billing_cycle = metadata.get("billing_cycle", "MONTHLY")

    if not tenant_id or not plan_code:
        return

    plan = await get_plan_by_code(db, plan_code)
    today = date.today()
    end_date = today + timedelta(days=365 if billing_cycle == "YEARLY" else 30)

    # Deactivate all existing active subscriptions
    await db.execute(
        update(SubscriptionHistory)
        .where(SubscriptionHistory.tenant_id == tenant_id, SubscriptionHistory.is_active == True)
        .values(is_active=False)
    )

    # Get old subscription
    old_sub_r = await db.execute(
        select(Tenant.subscription_id).where(Tenant.tenant_id == tenant_id)
    )
    old_sub_id = old_sub_r.scalar()

    # Create new subscription history
    history = SubscriptionHistory(
        tenant_id=tenant_id,
        subscription_id=plan.subscription_id,
        previous_subscription_id=old_sub_id,
        action="NEW" if old_sub_id == plan.subscription_id else "UPGRADE",
        start_date=today,
        end_date=end_date,
        billing_cycle=billing_cycle,
        amount_paid=session_data.get("amount_total", 0) / 100,  # Stripe uses cents
        payment_method="STRIPE",
        transaction_ref=session_data.get("id"),
        is_active=True,
    )
    db.add(history)

    # Update tenant
    await db.execute(
        update(Tenant)
        .where(Tenant.tenant_id == tenant_id)
        .values(
            subscription_id=plan.subscription_id,
            status="ACTIVE",
            trial_end_date=None,
        )
    )
    await db.commit()


async def _handle_subscription_updated(db: AsyncSession, subscription_data: dict):
    metadata = subscription_data.get("metadata", {})
    tenant_id = int(metadata.get("tenant_id", 0))
    if not tenant_id:
        return
    # In production: sync subscription status, next billing date etc.
    status = subscription_data.get("status")
    if status == "active":
        await db.execute(
            update(Tenant).where(Tenant.tenant_id == tenant_id).values(status="ACTIVE")
        )
        await db.commit()


async def _handle_subscription_cancelled(db: AsyncSession, subscription_data: dict):
    metadata = subscription_data.get("metadata", {})
    tenant_id = int(metadata.get("tenant_id", 0))
    if not tenant_id:
        return
    await db.execute(
        update(SubscriptionHistory)
        .where(SubscriptionHistory.tenant_id == tenant_id, SubscriptionHistory.is_active == True)
        .values(is_active=False)
    )
    await db.execute(
        update(Tenant).where(Tenant.tenant_id == tenant_id).values(status="CANCELLED")
    )
    await db.commit()


async def _handle_payment_failed(db: AsyncSession, invoice_data: dict):
    # In production: notify tenant, attempt retry logic
    pass
