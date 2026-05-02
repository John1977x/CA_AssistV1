from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from fastapi import HTTPException, status, Request
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple
import secrets

from app.models.auth import User, Tenant, Subscription, SubscriptionHistory, UserRole
from app.schemas.auth import (
    RegisterTenantRequest, LoginRequest, Token,
    ChangePasswordRequest, ForgotPasswordRequest, ResetPasswordRequest,
)
from app.core.security import (
    hash_password, verify_password, validate_password_strength,
    create_access_token, create_refresh_token, decode_token,
    create_invite_token, create_reset_token,
    generate_totp_secret, verify_totp, generate_totp_qr_base64,
)
from app.core.config import settings
from app.services.email import send_invite_email, send_reset_password_email, send_welcome_email


# ─── Registration ────────────────────────────────────────────────────────────

async def register_tenant(db: AsyncSession, data: RegisterTenantRequest) -> User:
    # Check email uniqueness
    existing = await db.execute(
        select(Tenant).where(Tenant.email == data.email)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered.")

    # Check tenant_code uniqueness
    code_check = await db.execute(
        select(Tenant).where(Tenant.tenant_code == data.tenant_code)
    )
    if code_check.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Firm code already taken. Try another.")

    # Validate password
    valid, msg = validate_password_strength(data.password)
    if not valid:
        raise HTTPException(status_code=400, detail=msg)

    # Get or create default trial subscription
    sub_result = await db.execute(
        select(Subscription).where(Subscription.plan_code == "TRIAL", Subscription.is_active == True)
    )
    subscription = sub_result.scalar_one_or_none()
    if not subscription:
        # Create a default trial plan if none exists
        subscription = Subscription(
            plan_name="Trial",
            plan_code="TRIAL",
            price_monthly=0,
            max_users=3,
            max_clients=10,
            max_branches=1,
            trial_days=14,
            features_json={"gst": True, "itr": True, "tds": False, "audit": False},
        )
        db.add(subscription)
        await db.flush()

    # Create tenant
    from datetime import date
    tenant = Tenant(
        subscription_id=subscription.subscription_id,
        tenant_code=data.tenant_code,
        firm_name=data.firm_name,
        owner_name=data.owner_name,
        email=data.email,
        phone=data.phone,
        membership_number=data.membership_number,
        status="TRIAL",
        trial_end_date=date.today() + timedelta(days=subscription.trial_days),
    )
    db.add(tenant)
    await db.flush()

    # Create default OWNER role for tenant
    owner_role = UserRole(
        tenant_id=tenant.tenant_id,
        role_name="Owner",
        role_code="OWNER",
        description="Full access to all modules",
        permissions_json={
            "gst": {"read": True, "write": True, "delete": True, "approve": True},
            "itr": {"read": True, "write": True, "delete": True, "approve": True},
            "tds": {"read": True, "write": True, "delete": True, "approve": True},
            "task": {"read": True, "write": True, "delete": True, "approve": True},
            "client": {"read": True, "write": True, "delete": True, "approve": True},
            "billing": {"read": True, "write": True, "delete": True, "approve": True},
            "user": {"read": True, "write": True, "delete": True, "approve": True},
            "report": {"read": True, "write": True, "delete": True, "approve": True},
        },
        is_system_role=False,
        can_manage_users=True,
        can_view_billing=True,
        can_approve_task=True,
    )
    db.add(owner_role)
    await db.flush()

    # Create owner user
    user = User(
        tenant_id=tenant.tenant_id,
        role_id=owner_role.role_id,
        first_name=data.owner_name.split()[0],
        last_name=" ".join(data.owner_name.split()[1:]) or data.owner_name.split()[0],
        display_name=data.owner_name,
        email=data.email,
        phone=data.phone,
        password_hash=hash_password(data.password),
        is_owner=True,
        status="ACTIVE",
        password_changed_at=datetime.now(timezone.utc),
    )
    db.add(user)
    await db.flush()

    # Subscription history
    sub_history = SubscriptionHistory(
        tenant_id=tenant.tenant_id,
        subscription_id=subscription.subscription_id,
        action="TRIAL",
        start_date=date.today(),
        end_date=tenant.trial_end_date,
        billing_cycle="MONTHLY",
        amount_paid=0,
        is_active=True,
    )
    db.add(sub_history)
    await db.commit()
    await db.refresh(user)

    # Send welcome email (non-blocking)
    try:
        await send_welcome_email(data.email, data.owner_name, data.firm_name)
    except Exception:
        pass

    return user


# ─── Login ───────────────────────────────────────────────────────────────────

async def authenticate_user(
    db: AsyncSession, data: LoginRequest, ip_address: str, user_agent: str
) -> Tuple[User, str, str]:
    # Find user
    result = await db.execute(
        select(User).where(
            User.email == data.email,
            User.is_deleted == False,
        )
    )
    user = result.scalar_one_or_none()

    now = datetime.now(timezone.utc)

    async def log_failure(reason: str):
        if user:
            await db.execute(
                update(User)
                .where(User.user_id == user.user_id)
                .values(failed_login_attempts=User.failed_login_attempts + 1)
            )
            if user.failed_login_attempts + 1 >= settings.MAX_LOGIN_ATTEMPTS:
                lockout_until = now + timedelta(minutes=settings.LOCKOUT_MINUTES)
                await db.execute(
                    update(User)
                    .where(User.user_id == user.user_id)
                    .values(locked_until=lockout_until)
                )
            await _write_log(db, user.tenant_id, user.user_id, "LOGIN_FAILED", ip_address, user_agent, False, reason)
        await db.commit()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    # Lockout check
    if user.locked_until and user.locked_until > now:
        remaining = int((user.locked_until - now).total_seconds() / 60)
        raise HTTPException(
            status_code=403,
            detail=f"Account locked. Try again in {remaining} minute(s).",
        )

    # Status check
    if user.status == "INACTIVE":
        raise HTTPException(status_code=403, detail="Account is inactive. Contact your administrator.")
    if user.status == "INVITED":
        raise HTTPException(status_code=403, detail="Please accept your invitation to activate account.")

    # Password check
    if not verify_password(data.password, user.password_hash):
        await log_failure("Wrong password")
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    # 2FA check
    if user.is_two_factor_enabled:
        if not data.totp_code:
            raise HTTPException(status_code=200, detail="2FA_REQUIRED", headers={"X-2FA-Required": "true"})
        if not verify_totp(user.two_factor_secret, data.totp_code):
            await log_failure("Invalid 2FA code")
            raise HTTPException(status_code=401, detail="Invalid 2FA code.")

    # Success — reset failed attempts
    await db.execute(
        update(User)
        .where(User.user_id == user.user_id)
        .values(
            failed_login_attempts=0,
            locked_until=None,
            last_login_at=now,
            last_login_ip=ip_address,
        )
    )

    extra = {"tenant_id": user.tenant_id, "role_id": user.role_id, "is_owner": user.is_owner}
    access_token = create_access_token(user.user_id, extra)
    refresh_token = create_refresh_token(user.user_id)

    await _write_log(db, user.tenant_id, user.user_id, "LOGIN", ip_address, user_agent, True)
    await db.commit()

    return user, access_token, refresh_token


async def refresh_access_token(db: AsyncSession, refresh_token: str) -> Tuple[str, str]:
    from jose import JWTError
    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type.")
        user_id = int(payload["sub"])
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token.")

    result = await db.execute(
        select(User).where(User.user_id == user_id, User.is_deleted == False, User.status == "ACTIVE")
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found.")

    extra = {"tenant_id": user.tenant_id, "role_id": user.role_id, "is_owner": user.is_owner}
    new_access = create_access_token(user.user_id, extra)
    new_refresh = create_refresh_token(user.user_id)
    return new_access, new_refresh


# ─── Password Management ─────────────────────────────────────────────────────

async def change_password(db: AsyncSession, user: User, data: ChangePasswordRequest):
    if not verify_password(data.current_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect.")
    valid, msg = validate_password_strength(data.new_password)
    if not valid:
        raise HTTPException(status_code=400, detail=msg)
    await db.execute(
        update(User)
        .where(User.user_id == user.user_id)
        .values(
            password_hash=hash_password(data.new_password),
            password_changed_at=datetime.now(timezone.utc),
        )
    )
    await db.commit()


async def forgot_password(db: AsyncSession, email: str):
    result = await db.execute(
        select(User).where(User.email == email, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()
    if not user:
        return  # Silent — don't reveal if email exists

    token = create_reset_token()
    expiry = datetime.now(timezone.utc) + timedelta(hours=2)

    await db.execute(
        update(User)
        .where(User.user_id == user.user_id)
        .values(invite_token=token, invite_expiry=expiry)
    )
    await db.commit()

    try:
        await send_reset_password_email(user.email, user.display_name or user.first_name, token)
    except Exception:
        pass


async def reset_password(db: AsyncSession, token: str, new_password: str):
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(User).where(
            User.invite_token == token,
            User.invite_expiry > now,
            User.is_deleted == False,
        )
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset link.")

    valid, msg = validate_password_strength(new_password)
    if not valid:
        raise HTTPException(status_code=400, detail=msg)

    await db.execute(
        update(User)
        .where(User.user_id == user.user_id)
        .values(
            password_hash=hash_password(new_password),
            password_changed_at=now,
            invite_token=None,
            invite_expiry=None,
            failed_login_attempts=0,
            locked_until=None,
        )
    )
    await db.commit()


# ─── 2FA ────────────────────────────────────────────────────────────────────

async def enable_2fa(db: AsyncSession, user: User) -> Tuple[str, str]:
    secret = generate_totp_secret()
    qr = generate_totp_qr_base64(secret, user.email)
    # Temporarily store secret; confirm after user verifies TOTP
    await db.execute(
        update(User)
        .where(User.user_id == user.user_id)
        .values(two_factor_secret=secret)  # Not enabled yet — pending verify
    )
    await db.commit()
    return qr, secret


async def confirm_2fa(db: AsyncSession, user: User, code: str):
    if not user.two_factor_secret:
        raise HTTPException(status_code=400, detail="2FA setup not initiated.")
    if not verify_totp(user.two_factor_secret, code):
        raise HTTPException(status_code=400, detail="Invalid TOTP code. Please try again.")
    await db.execute(
        update(User)
        .where(User.user_id == user.user_id)
        .values(is_two_factor_enabled=True)
    )
    await db.commit()


async def disable_2fa(db: AsyncSession, user: User, code: str):
    if not user.is_two_factor_enabled:
        raise HTTPException(status_code=400, detail="2FA is not enabled.")
    if not verify_totp(user.two_factor_secret, code):
        raise HTTPException(status_code=400, detail="Invalid TOTP code.")
    await db.execute(
        update(User)
        .where(User.user_id == user.user_id)
        .values(is_two_factor_enabled=False, two_factor_secret=None)
    )
    await db.commit()


# ─── Internal Helpers ────────────────────────────────────────────────────────

async def _write_log(
    db: AsyncSession,
    tenant_id: int,
    user_id: Optional[int],
    action: str,
    ip: str,
    ua: str,
    success: bool,
    error: str = None,
):
    from app.models.auth import UserLog
    log = UserLog(
        tenant_id=tenant_id,
        user_id=user_id,
        action=action,
        module="AUTH",
        ip_address=ip,
        user_agent=ua,
        is_success=success,
        error_message=error,
    )
    db.add(log)
