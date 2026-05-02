"""Initial migration - auth tables

Revision ID: 001_initial_auth
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001_initial_auth"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── subscription ────────────────────────────────────────────────────────
    op.create_table(
        "subscription",
        sa.Column("subscription_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("plan_name", sa.String(100), nullable=False),
        sa.Column("plan_code", sa.String(20), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price_monthly", sa.Numeric(10, 2), nullable=False),
        sa.Column("price_yearly", sa.Numeric(10, 2), nullable=True),
        sa.Column("max_users", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("max_clients", sa.Integer(), nullable=True),
        sa.Column("max_branches", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("storage_limit_gb", sa.Numeric(6, 2), nullable=True),
        sa.Column("features_json", postgresql.JSONB(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("trial_days", sa.Integer(), nullable=False, server_default="14"),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("subscription_id", name="pk_subscription"),
        sa.UniqueConstraint("plan_code", name="uq_subscription_plan_code"),
    )

    # ── tenant ──────────────────────────────────────────────────────────────
    op.create_table(
        "tenant",
        sa.Column("tenant_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("subscription_id", sa.Integer(), nullable=False),
        sa.Column("tenant_code", sa.String(30), nullable=False),
        sa.Column("firm_name", sa.String(200), nullable=False),
        sa.Column("owner_name", sa.String(150), nullable=False),
        sa.Column("email", sa.String(150), nullable=False),
        sa.Column("phone", sa.String(15), nullable=False),
        sa.Column("alternate_phone", sa.String(15), nullable=True),
        sa.Column("membership_number", sa.String(50), nullable=True),
        sa.Column("gstin", sa.String(15), nullable=True),
        sa.Column("pan", sa.String(10), nullable=True),
        sa.Column("address_line1", sa.String(250), nullable=True),
        sa.Column("address_line2", sa.String(250), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("state", sa.String(100), nullable=True),
        sa.Column("pincode", sa.String(10), nullable=True),
        sa.Column("country", sa.String(100), nullable=False, server_default="India"),
        sa.Column("logo_url", sa.Text(), nullable=True),
        sa.Column("timezone", sa.String(60), nullable=False, server_default="Asia/Kolkata"),
        sa.Column("currency_code", sa.String(3), nullable=False, server_default="INR"),
        sa.Column("financial_year_start", sa.SmallInteger(), nullable=False, server_default="4"),
        sa.Column("status", sa.String(20), nullable=False, server_default="ACTIVE"),
        sa.Column("trial_end_date", sa.Date(), nullable=True),
        sa.Column("onboarded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.ForeignKeyConstraint(["subscription_id"], ["subscription.subscription_id"], name="fk_tenant_subscription_id_subscription"),
        sa.PrimaryKeyConstraint("tenant_id", name="pk_tenant"),
        sa.UniqueConstraint("tenant_code", name="uq_tenant_tenant_code"),
        sa.UniqueConstraint("email", name="uq_tenant_email"),
    )
    op.create_index("ix_tenant_email", "tenant", ["email"])
    op.create_index("ix_tenant_status", "tenant", ["status"])

    # ── subscription_history ─────────────────────────────────────────────────
    op.create_table(
        "subscription_history",
        sa.Column("history_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("subscription_id", sa.Integer(), nullable=False),
        sa.Column("previous_subscription_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(30), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("billing_cycle", sa.String(10), nullable=False, server_default="MONTHLY"),
        sa.Column("amount_paid", sa.Numeric(10, 2), nullable=True),
        sa.Column("payment_method", sa.String(50), nullable=True),
        sa.Column("transaction_ref", sa.String(100), nullable=True),
        sa.Column("invoice_number", sa.String(50), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenant.tenant_id"], name="fk_subscription_history_tenant_id_tenant"),
        sa.ForeignKeyConstraint(["subscription_id"], ["subscription.subscription_id"], name="fk_subscription_history_subscription_id_subscription"),
        sa.PrimaryKeyConstraint("history_id", name="pk_subscription_history"),
    )

    # ── user_role ───────────────────────────────────────────────────────────
    op.create_table(
        "user_role",
        sa.Column("role_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=True),
        sa.Column("role_name", sa.String(100), nullable=False),
        sa.Column("role_code", sa.String(30), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("permissions_json", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("is_system_role", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("can_manage_users", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("can_view_billing", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("can_approve_task", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenant.tenant_id"], name="fk_user_role_tenant_id_tenant"),
        sa.PrimaryKeyConstraint("role_id", name="pk_user_role"),
    )

    # ── branch (no FK to user yet — user table not created) ─────────────────
    op.create_table(
        "branch",
        sa.Column("branch_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("branch_name", sa.String(150), nullable=False),
        sa.Column("branch_code", sa.String(20), nullable=False),
        sa.Column("manager_user_id", sa.Integer(), nullable=True),
        sa.Column("email", sa.String(150), nullable=True),
        sa.Column("phone", sa.String(15), nullable=True),
        sa.Column("address_line1", sa.String(250), nullable=True),
        sa.Column("address_line2", sa.String(250), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("state", sa.String(100), nullable=True),
        sa.Column("pincode", sa.String(10), nullable=True),
        sa.Column("gstin", sa.String(15), nullable=True),
        sa.Column("is_head_office", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenant.tenant_id"], name="fk_branch_tenant_id_tenant"),
        sa.PrimaryKeyConstraint("branch_id", name="pk_branch"),
    )

    # ── user ────────────────────────────────────────────────────────────────
    op.create_table(
        "user",
        sa.Column("user_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("branch_id", sa.Integer(), nullable=True),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("display_name", sa.String(200), nullable=True),
        sa.Column("email", sa.String(150), nullable=False),
        sa.Column("phone", sa.String(15), nullable=True),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("avatar_url", sa.Text(), nullable=True),
        sa.Column("designation", sa.String(100), nullable=True),
        sa.Column("membership_number", sa.String(50), nullable=True),
        sa.Column("is_owner", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_two_factor_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("two_factor_secret", sa.Text(), nullable=True),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_login_ip", sa.String(45), nullable=True),
        sa.Column("password_changed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_login_attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="ACTIVE"),
        sa.Column("invite_token", sa.String(100), nullable=True),
        sa.Column("invite_expiry", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notification_prefs_json", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenant.tenant_id"], name="fk_user_tenant_id_tenant"),
        sa.ForeignKeyConstraint(["role_id"], ["user_role.role_id"], name="fk_user_role_id_user_role"),
        sa.ForeignKeyConstraint(["branch_id"], ["branch.branch_id"], name="fk_user_branch_id_branch"),
        sa.PrimaryKeyConstraint("user_id", name="pk_user"),
    )
    op.create_index("ix_user_email", "user", ["email"])
    op.create_index("ix_user_tenant_id", "user", ["tenant_id"])
    op.create_index("ix_user_status", "user", ["status"])

    # Add manager FK to branch now that user table exists
    op.create_foreign_key(
        "fk_branch_manager_user_id_user", "branch", "user", ["manager_user_id"], ["user_id"]
    )

    # ── user_log ────────────────────────────────────────────────────────────
    op.create_table(
        "user_log",
        sa.Column("log_id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("module", sa.String(60), nullable=False),
        sa.Column("entity_type", sa.String(60), nullable=True),
        sa.Column("entity_id", sa.Integer(), nullable=True),
        sa.Column("old_value_json", postgresql.JSONB(), nullable=True),
        sa.Column("new_value_json", postgresql.JSONB(), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("session_id", sa.String(100), nullable=True),
        sa.Column("is_success", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenant.tenant_id"], name="fk_user_log_tenant_id_tenant"),
        sa.ForeignKeyConstraint(["user_id"], ["user.user_id"], name="fk_user_log_user_id_user"),
        sa.PrimaryKeyConstraint("log_id", name="pk_user_log"),
    )
    op.create_index("ix_user_log_tenant_id", "user_log", ["tenant_id"])
    op.create_index("ix_user_log_user_id", "user_log", ["user_id"])
    op.create_index("ix_user_log_created_at", "user_log", ["created_at"])

    # ── seed default subscription plans ────────────────────────────────────
    op.execute("""
        INSERT INTO subscription (plan_name, plan_code, description, price_monthly, price_yearly,
            max_users, max_clients, max_branches, storage_limit_gb, features_json, trial_days, sort_order)
        VALUES
        ('Trial', 'TRIAL', '14-day free trial with full access', 0, 0,
            3, 10, 1, 1,
            '{"gst": true, "itr": true, "tds": false, "audit": false, "investment": false}',
            14, 0),
        ('Basic', 'BASIC', 'For solo practitioners', 999, 9990,
            5, 50, 1, 5,
            '{"gst": true, "itr": true, "tds": true, "audit": false, "investment": false}',
            14, 1),
        ('Pro', 'PRO', 'For growing CA firms', 2499, 24990,
            15, 200, 3, 20,
            '{"gst": true, "itr": true, "tds": true, "audit": true, "investment": true}',
            14, 2),
        ('Enterprise', 'ENT', 'For large multi-branch firms', 4999, 49990,
            100, 2000, 10, 100,
            '{"gst": true, "itr": true, "tds": true, "audit": true, "investment": true, "api_access": true}',
            14, 3)
    """)


def downgrade() -> None:
    op.drop_table("user_log")
    op.drop_constraint("fk_branch_manager_user_id_user", "branch", type_="foreignkey")
    op.drop_table("user")
    op.drop_table("branch")
    op.drop_table("user_role")
    op.drop_table("subscription_history")
    op.drop_table("tenant")
    op.drop_table("subscription")
