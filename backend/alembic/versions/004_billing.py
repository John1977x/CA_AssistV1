"""Add billing tables - invoice, line items, time log, expense, payment

Revision ID: 004_billing
Revises: 003_task_workflow
Create Date: 2024-01-04 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "004_billing"
down_revision: Union[str, None] = "003_task_workflow"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── invoice ───────────────────────────────────────────────────────────────
    op.create_table(
        "invoice",
        sa.Column("invoice_id",           sa.Integer(),        autoincrement=True, nullable=False),
        sa.Column("tenant_id",            sa.Integer(),        nullable=False),
        sa.Column("customer_id",          sa.Integer(),        nullable=False),
        sa.Column("branch_id",            sa.Integer(),        nullable=True),
        sa.Column("task_id",              sa.Integer(),        nullable=True),
        sa.Column("invoice_number",       sa.String(50),       nullable=False),
        sa.Column("invoice_date",         sa.Date(),           nullable=False),
        sa.Column("due_date",             sa.Date(),           nullable=False),
        sa.Column("subtotal",             sa.Numeric(12, 2),   nullable=False, server_default="0"),
        sa.Column("discount_pct",         sa.Numeric(5, 2),    server_default="0"),
        sa.Column("discount_amount",      sa.Numeric(12, 2),   server_default="0"),
        sa.Column("taxable_amount",       sa.Numeric(12, 2),   nullable=False, server_default="0"),
        sa.Column("cgst_amount",          sa.Numeric(10, 2),   server_default="0"),
        sa.Column("sgst_amount",          sa.Numeric(10, 2),   server_default="0"),
        sa.Column("igst_amount",          sa.Numeric(10, 2),   server_default="0"),
        sa.Column("total_tax",            sa.Numeric(10, 2),   server_default="0"),
        sa.Column("total_amount",         sa.Numeric(12, 2),   nullable=False, server_default="0"),
        sa.Column("amount_paid",          sa.Numeric(12, 2),   nullable=False, server_default="0"),
        sa.Column("balance_due",          sa.Numeric(12, 2),   nullable=False, server_default="0"),
        sa.Column("currency_code",        sa.String(3),        nullable=False, server_default="INR"),
        sa.Column("place_of_supply",      sa.String(50),       nullable=True),
        sa.Column("is_igst",              sa.Boolean(),        nullable=False, server_default=sa.false()),
        sa.Column("gst_rate_pct",         sa.Numeric(5, 2),    server_default="18"),
        sa.Column("reverse_charge",       sa.Boolean(),        nullable=False, server_default=sa.false()),
        sa.Column("status",               sa.String(20),       nullable=False, server_default="DRAFT"),
        sa.Column("payment_terms_days",   sa.Integer(),        server_default="30"),
        sa.Column("notes",                sa.Text(),           nullable=True),
        sa.Column("terms_conditions",     sa.Text(),           nullable=True),
        sa.Column("internal_notes",       sa.Text(),           nullable=True),
        sa.Column("tally_voucher_number", sa.String(100),      nullable=True),
        sa.Column("tally_synced_at",      sa.DateTime(timezone=True), nullable=True),
        sa.Column("zoho_invoice_id",      sa.String(100),      nullable=True),
        sa.Column("qb_invoice_id",        sa.String(100),      nullable=True),
        sa.Column("sent_at",              sa.DateTime(timezone=True), nullable=True),
        sa.Column("sent_by_user_id",      sa.Integer(),        nullable=True),
        sa.Column("created_by_user_id",   sa.Integer(),        nullable=True),
        sa.Column("created_at",  sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at",  sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("is_deleted",           sa.Boolean(),        nullable=False, server_default=sa.false()),
        sa.ForeignKeyConstraint(["tenant_id"],          ["tenant.tenant_id"],   name="fk_invoice_tenant"),
        sa.ForeignKeyConstraint(["customer_id"],        ["customer.customer_id"], name="fk_invoice_customer"),
        sa.ForeignKeyConstraint(["branch_id"],          ["branch.branch_id"],   name="fk_invoice_branch"),
        sa.ForeignKeyConstraint(["task_id"],            ["task.task_id"],       name="fk_invoice_task"),
        sa.ForeignKeyConstraint(["sent_by_user_id"],    ["user.user_id"],       name="fk_invoice_sent_by"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["user.user_id"],       name="fk_invoice_created_by"),
        sa.PrimaryKeyConstraint("invoice_id", name="pk_invoice"),
    )
    op.create_index("ix_invoice_tenant_id",   "invoice", ["tenant_id"])
    op.create_index("ix_invoice_customer_id", "invoice", ["customer_id"])
    op.create_index("ix_invoice_status",      "invoice", ["status"])
    op.create_index("ix_invoice_due_date",    "invoice", ["due_date"])

    # ── invoice_line_item ─────────────────────────────────────────────────────
    op.create_table(
        "invoice_line_item",
        sa.Column("line_item_id",     sa.Integer(),       autoincrement=True, nullable=False),
        sa.Column("invoice_id",       sa.Integer(),       nullable=False),
        sa.Column("description",      sa.String(500),     nullable=False),
        sa.Column("hsn_sac_code",     sa.String(20),      nullable=True),
        sa.Column("quantity",         sa.Numeric(10, 3),  nullable=False, server_default="1"),
        sa.Column("unit",             sa.String(20),      nullable=True),
        sa.Column("unit_price",       sa.Numeric(12, 2),  nullable=False),
        sa.Column("discount_pct",     sa.Numeric(5, 2),   server_default="0"),
        sa.Column("taxable_amount",   sa.Numeric(12, 2),  nullable=False),
        sa.Column("gst_rate_pct",     sa.Numeric(5, 2),   server_default="18"),
        sa.Column("cgst_amount",      sa.Numeric(10, 2),  server_default="0"),
        sa.Column("sgst_amount",      sa.Numeric(10, 2),  server_default="0"),
        sa.Column("igst_amount",      sa.Numeric(10, 2),  server_default="0"),
        sa.Column("line_total",       sa.Numeric(12, 2),  nullable=False),
        sa.Column("sort_order",       sa.Integer(),       nullable=False, server_default="0"),
        sa.Column("task_id",          sa.Integer(),       nullable=True),
        sa.Column("time_log_ids",     postgresql.ARRAY(sa.Integer()), nullable=True),
        sa.ForeignKeyConstraint(["invoice_id"], ["invoice.invoice_id"], name="fk_line_item_invoice"),
        sa.ForeignKeyConstraint(["task_id"],    ["task.task_id"],       name="fk_line_item_task"),
        sa.PrimaryKeyConstraint("line_item_id", name="pk_invoice_line_item"),
    )
    op.create_index("ix_line_item_invoice_id", "invoice_line_item", ["invoice_id"])

    # ── time_log ──────────────────────────────────────────────────────────────
    op.create_table(
        "time_log",
        sa.Column("time_log_id",       sa.Integer(),     autoincrement=True, nullable=False),
        sa.Column("tenant_id",         sa.Integer(),     nullable=False),
        sa.Column("user_id",           sa.Integer(),     nullable=False),
        sa.Column("customer_id",       sa.Integer(),     nullable=False),
        sa.Column("task_id",           sa.Integer(),     nullable=True),
        sa.Column("log_date",          sa.Date(),        nullable=False),
        sa.Column("start_time",        sa.String(5),     nullable=True),
        sa.Column("end_time",          sa.String(5),     nullable=True),
        sa.Column("duration_minutes",  sa.Integer(),     nullable=False),
        sa.Column("billable_minutes",  sa.Integer(),     nullable=False),
        sa.Column("description",       sa.Text(),        nullable=False),
        sa.Column("is_billable",       sa.Boolean(),     nullable=False, server_default=sa.true()),
        sa.Column("is_billed",         sa.Boolean(),     nullable=False, server_default=sa.false()),
        sa.Column("invoice_id",        sa.Integer(),     nullable=True),
        sa.Column("hourly_rate",       sa.Numeric(10,2), nullable=True),
        sa.Column("line_amount",       sa.Numeric(10,2), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("is_deleted",        sa.Boolean(),     nullable=False, server_default=sa.false()),
        sa.ForeignKeyConstraint(["tenant_id"],   ["tenant.tenant_id"],     name="fk_time_log_tenant"),
        sa.ForeignKeyConstraint(["user_id"],     ["user.user_id"],         name="fk_time_log_user"),
        sa.ForeignKeyConstraint(["customer_id"], ["customer.customer_id"], name="fk_time_log_customer"),
        sa.ForeignKeyConstraint(["task_id"],     ["task.task_id"],         name="fk_time_log_task"),
        sa.ForeignKeyConstraint(["invoice_id"],  ["invoice.invoice_id"],   name="fk_time_log_invoice"),
        sa.PrimaryKeyConstraint("time_log_id", name="pk_time_log"),
    )
    op.create_index("ix_time_log_tenant_id",   "time_log", ["tenant_id"])
    op.create_index("ix_time_log_user_id",     "time_log", ["user_id"])
    op.create_index("ix_time_log_customer_id", "time_log", ["customer_id"])
    op.create_index("ix_time_log_log_date",    "time_log", ["log_date"])

    # ── expense ───────────────────────────────────────────────────────────────
    op.create_table(
        "expense",
        sa.Column("expense_id",           sa.Integer(),     autoincrement=True, nullable=False),
        sa.Column("tenant_id",            sa.Integer(),     nullable=False),
        sa.Column("user_id",              sa.Integer(),     nullable=False),
        sa.Column("customer_id",          sa.Integer(),     nullable=True),
        sa.Column("task_id",              sa.Integer(),     nullable=True),
        sa.Column("expense_date",         sa.Date(),        nullable=False),
        sa.Column("category",             sa.String(60),    nullable=False),
        sa.Column("description",          sa.Text(),        nullable=False),
        sa.Column("amount",               sa.Numeric(10,2), nullable=False),
        sa.Column("gst_amount",           sa.Numeric(10,2), server_default="0"),
        sa.Column("total_amount",         sa.Numeric(10,2), nullable=False),
        sa.Column("is_billable",          sa.Boolean(),     nullable=False, server_default=sa.false()),
        sa.Column("is_reimbursed",        sa.Boolean(),     nullable=False, server_default=sa.false()),
        sa.Column("receipt_url",          sa.Text(),        nullable=True),
        sa.Column("payment_mode",         sa.String(30),    nullable=True),
        sa.Column("vendor_name",          sa.String(200),   nullable=True),
        sa.Column("status",               sa.String(20),    nullable=False, server_default="PENDING"),
        sa.Column("approved_by_user_id",  sa.Integer(),     nullable=True),
        sa.Column("approved_at",          sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["tenant_id"],          ["tenant.tenant_id"],     name="fk_expense_tenant"),
        sa.ForeignKeyConstraint(["user_id"],            ["user.user_id"],         name="fk_expense_user"),
        sa.ForeignKeyConstraint(["customer_id"],        ["customer.customer_id"], name="fk_expense_customer"),
        sa.ForeignKeyConstraint(["task_id"],            ["task.task_id"],         name="fk_expense_task"),
        sa.ForeignKeyConstraint(["approved_by_user_id"],["user.user_id"],         name="fk_expense_approved_by"),
        sa.PrimaryKeyConstraint("expense_id", name="pk_expense"),
    )
    op.create_index("ix_expense_tenant_id", "expense", ["tenant_id"])
    op.create_index("ix_expense_user_id",   "expense", ["user_id"])

    # ── payment_received ──────────────────────────────────────────────────────
    op.create_table(
        "payment_received",
        sa.Column("payment_id",           sa.Integer(),     autoincrement=True, nullable=False),
        sa.Column("tenant_id",            sa.Integer(),     nullable=False),
        sa.Column("invoice_id",           sa.Integer(),     nullable=False),
        sa.Column("customer_id",          sa.Integer(),     nullable=False),
        sa.Column("payment_date",         sa.Date(),        nullable=False),
        sa.Column("amount",               sa.Numeric(12,2), nullable=False),
        sa.Column("payment_mode",         sa.String(30),    nullable=False),
        sa.Column("reference_number",     sa.String(100),   nullable=True),
        sa.Column("bank_name",            sa.String(100),   nullable=True),
        sa.Column("notes",                sa.Text(),        nullable=True),
        sa.Column("tds_deducted",         sa.Numeric(10,2), server_default="0"),
        sa.Column("net_received",         sa.Numeric(12,2), nullable=False),
        sa.Column("recorded_by_user_id",  sa.Integer(),     nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["tenant_id"],           ["tenant.tenant_id"],     name="fk_payment_tenant"),
        sa.ForeignKeyConstraint(["invoice_id"],          ["invoice.invoice_id"],   name="fk_payment_invoice"),
        sa.ForeignKeyConstraint(["customer_id"],         ["customer.customer_id"], name="fk_payment_customer"),
        sa.ForeignKeyConstraint(["recorded_by_user_id"], ["user.user_id"],         name="fk_payment_recorded_by"),
        sa.PrimaryKeyConstraint("payment_id", name="pk_payment_received"),
    )
    op.create_index("ix_payment_tenant_id",   "payment_received", ["tenant_id"])
    op.create_index("ix_payment_invoice_id",  "payment_received", ["invoice_id"])


def downgrade() -> None:
    op.drop_table("payment_received")
    op.drop_table("expense")
    op.drop_table("time_log")
    op.drop_table("invoice_line_item")
    op.drop_table("invoice")
