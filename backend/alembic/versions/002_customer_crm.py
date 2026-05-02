"""Add customer, customer_details, enquiry tables

Revision ID: 002_customer_crm
Revises: 001_initial_auth
Create Date: 2024-01-02 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "002_customer_crm"
down_revision: Union[str, None] = "001_initial_auth"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── customer ─────────────────────────────────────────────────────────────
    op.create_table(
        "customer",
        sa.Column("customer_id",             sa.Integer(),           autoincrement=True, nullable=False),
        sa.Column("tenant_id",               sa.Integer(),           nullable=False),
        sa.Column("branch_id",               sa.Integer(),           nullable=True),
        sa.Column("assigned_user_id",        sa.Integer(),           nullable=True),
        sa.Column("customer_code",           sa.String(30),          nullable=False),
        sa.Column("customer_type",           sa.String(30),          nullable=False, server_default="INDIVIDUAL"),
        sa.Column("display_name",            sa.String(200),         nullable=False),
        sa.Column("legal_name",              sa.String(200),         nullable=True),
        sa.Column("pan",                     sa.String(10),          nullable=True),
        sa.Column("gstin",                   sa.String(15),          nullable=True),
        sa.Column("aadhar_number",           sa.String(12),          nullable=True),
        sa.Column("email",                   sa.String(150),         nullable=True),
        sa.Column("phone",                   sa.String(15),          nullable=False),
        sa.Column("alternate_phone",         sa.String(15),          nullable=True),
        sa.Column("whatsapp",                sa.String(15),          nullable=True),
        sa.Column("date_of_birth",           sa.Date(),              nullable=True),
        sa.Column("date_of_incorporation",   sa.Date(),              nullable=True),
        sa.Column("industry_code",           sa.String(60),          nullable=True),
        sa.Column("source_channel",          sa.String(50),          nullable=True),
        sa.Column("referred_by_customer_id", sa.Integer(),           nullable=True),
        sa.Column("tags",                    postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("portal_access",           sa.Boolean(),           nullable=False, server_default=sa.false()),
        sa.Column("portal_email",            sa.String(150),         nullable=True),
        sa.Column("status",                  sa.String(20),          nullable=False, server_default="ACTIVE"),
        sa.Column("risk_level",              sa.String(10),          nullable=True),
        sa.Column("kyc_status",              sa.String(20),          nullable=False, server_default="PENDING"),
        sa.Column("kyc_verified_at",         sa.DateTime(timezone=True), nullable=True),
        sa.Column("onboarded_at",            sa.Date(),              nullable=True),
        sa.Column("notes",                   sa.Text(),              nullable=True),
        sa.Column("created_at",              sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at",              sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("is_deleted",              sa.Boolean(),           nullable=False, server_default=sa.false()),
        sa.ForeignKeyConstraint(["tenant_id"],               ["tenant.tenant_id"],   name="fk_customer_tenant_id_tenant"),
        sa.ForeignKeyConstraint(["branch_id"],               ["branch.branch_id"],   name="fk_customer_branch_id_branch"),
        sa.ForeignKeyConstraint(["assigned_user_id"],        ["user.user_id"],       name="fk_customer_assigned_user_id_user"),
        sa.ForeignKeyConstraint(["referred_by_customer_id"], ["customer.customer_id"], name="fk_customer_referred_by_customer_id_customer"),
        sa.PrimaryKeyConstraint("customer_id", name="pk_customer"),
    )
    op.create_index("ix_customer_tenant_id",   "customer", ["tenant_id"])
    op.create_index("ix_customer_pan",         "customer", ["pan"])
    op.create_index("ix_customer_gstin",       "customer", ["gstin"])
    op.create_index("ix_customer_phone",       "customer", ["phone"])
    op.create_index("ix_customer_status",      "customer", ["status"])
    op.create_index("ix_customer_kyc_status",  "customer", ["kyc_status"])

    # ── customer_details ──────────────────────────────────────────────────────
    op.create_table(
        "customer_details",
        sa.Column("customer_detail_id",        sa.Integer(),  autoincrement=True, nullable=False),
        sa.Column("customer_id",               sa.Integer(),  nullable=False),
        sa.Column("registered_address_line1",  sa.String(250), nullable=True),
        sa.Column("registered_address_line2",  sa.String(250), nullable=True),
        sa.Column("registered_city",           sa.String(100), nullable=True),
        sa.Column("registered_state",          sa.String(100), nullable=True),
        sa.Column("registered_pincode",        sa.String(10),  nullable=True),
        sa.Column("communication_address",     sa.Text(),      nullable=True),
        sa.Column("bank_name",                 sa.String(100), nullable=True),
        sa.Column("bank_account_number",       sa.String(20),  nullable=True),
        sa.Column("bank_ifsc",                 sa.String(11),  nullable=True),
        sa.Column("bank_account_type",         sa.String(20),  nullable=True),
        sa.Column("income_tax_status",         sa.String(30),  nullable=True),
        sa.Column("gst_registration_type",     sa.String(30),  nullable=True),
        sa.Column("gst_registration_date",     sa.Date(),      nullable=True),
        sa.Column("gst_cancellation_date",     sa.Date(),      nullable=True),
        sa.Column("tds_deductor_type",         sa.String(50),  nullable=True),
        sa.Column("director_partners_json",    postgresql.JSONB(), nullable=True),
        sa.Column("filing_history_json",       postgresql.JSONB(), nullable=True),
        sa.Column("documents_json",            postgresql.JSONB(), nullable=True),
        sa.Column("custom_fields_json",        postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["customer_id"], ["customer.customer_id"], name="fk_customer_details_customer_id_customer"),
        sa.PrimaryKeyConstraint("customer_detail_id", name="pk_customer_details"),
        sa.UniqueConstraint("customer_id", name="uq_customer_details_customer_id"),
    )

    # ── enquiry ───────────────────────────────────────────────────────────────
    op.create_table(
        "enquiry",
        sa.Column("enquiry_id",              sa.Integer(),  autoincrement=True, nullable=False),
        sa.Column("tenant_id",               sa.Integer(),  nullable=False),
        sa.Column("branch_id",               sa.Integer(),  nullable=True),
        sa.Column("assigned_to_user_id",     sa.Integer(),  nullable=True),
        sa.Column("enquiry_date",            sa.Date(),     nullable=False, server_default=sa.func.current_date()),
        sa.Column("enquiry_number",          sa.String(30), nullable=False),
        sa.Column("full_name",               sa.String(200), nullable=False),
        sa.Column("email",                   sa.String(150), nullable=True),
        sa.Column("phone",                   sa.String(15),  nullable=False),
        sa.Column("company_name",            sa.String(200), nullable=True),
        sa.Column("service_interested",      postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("source",                  sa.String(50),  nullable=True),
        sa.Column("referred_by_customer_id", sa.Integer(),   nullable=True),
        sa.Column("message",                 sa.Text(),      nullable=True),
        sa.Column("estimated_value",         sa.Numeric(10, 2), nullable=True),
        sa.Column("status",                  sa.String(20),  nullable=False, server_default="NEW"),
        sa.Column("follow_up_date",          sa.Date(),      nullable=True),
        sa.Column("follow_up_notes",         sa.Text(),      nullable=True),
        sa.Column("lost_reason",             sa.String(200), nullable=True),
        sa.Column("is_converted",            sa.Boolean(),   nullable=False, server_default=sa.false()),
        sa.Column("converted_customer_id",   sa.Integer(),   nullable=True),
        sa.Column("converted_at",            sa.DateTime(timezone=True), nullable=True),
        sa.Column("converted_by_user_id",    sa.Integer(),   nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["tenant_id"],               ["tenant.tenant_id"],    name="fk_enquiry_tenant_id_tenant"),
        sa.ForeignKeyConstraint(["branch_id"],               ["branch.branch_id"],    name="fk_enquiry_branch_id_branch"),
        sa.ForeignKeyConstraint(["assigned_to_user_id"],     ["user.user_id"],        name="fk_enquiry_assigned_to_user_id_user"),
        sa.ForeignKeyConstraint(["referred_by_customer_id"], ["customer.customer_id"], name="fk_enquiry_referred_by_customer_id_customer"),
        sa.ForeignKeyConstraint(["converted_customer_id"],   ["customer.customer_id"], name="fk_enquiry_converted_customer_id_customer"),
        sa.ForeignKeyConstraint(["converted_by_user_id"],    ["user.user_id"],        name="fk_enquiry_converted_by_user_id_user"),
        sa.PrimaryKeyConstraint("enquiry_id", name="pk_enquiry"),
    )
    op.create_index("ix_enquiry_tenant_id",  "enquiry", ["tenant_id"])
    op.create_index("ix_enquiry_status",     "enquiry", ["status"])
    op.create_index("ix_enquiry_phone",      "enquiry", ["phone"])


def downgrade() -> None:
    op.drop_table("enquiry")
    op.drop_table("customer_details")
    op.drop_table("customer")
