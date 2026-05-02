"""Add company tables for multi-company architecture

Revision ID: 006_add_company
Revises: 004_billing
Create Date: 2026-05-01

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = '006_add_company'
down_revision = '004_billing'
branch_labels = None
depends_on = None


def upgrade():
    # ─── Company ────────────────────────────────────────────────────────────
    op.create_table(
        'company',
        sa.Column('company_id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('owner_id', sa.Integer, sa.ForeignKey('user.user_id'), nullable=False, index=True),
        sa.Column('company_code', sa.String(20), nullable=False, unique=True),
        sa.Column('company_name', sa.String(200), nullable=False, index=True),
        sa.Column('email', sa.String(150)),
        sa.Column('phone', sa.String(20)),
        sa.Column('address_line1', sa.String(200)),
        sa.Column('address_line2', sa.String(200)),
        sa.Column('city', sa.String(100)),
        sa.Column('state', sa.String(100)),
        sa.Column('pincode', sa.String(10)),
        sa.Column('country', sa.String(100), default='India'),
        sa.Column('pan', sa.String(10)),
        sa.Column('gstin', sa.String(15)),
        sa.Column('cin', sa.String(21)),
        sa.Column('status', sa.String(20), nullable=False, default='ACTIVE'),
        sa.Column('description', sa.Text),
        sa.Column('logo_url', sa.String(500)),
        sa.Column('website', sa.String(200)),
        sa.Column('extra_data', postgresql.JSONB, default={}),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('is_deleted', sa.Boolean, nullable=False, default=False)
    )

    # ─── Company Branch ─────────────────────────────────────────────────────
    op.create_table(
        'company_branch',
        sa.Column('branch_id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('company.company_id'), nullable=False, index=True),
        sa.Column('manager_id', sa.Integer, sa.ForeignKey('user.user_id')),
        sa.Column('branch_name', sa.String(200), nullable=False, index=True),
        sa.Column('branch_code', sa.String(20), nullable=False),
        sa.Column('email', sa.String(150)),
        sa.Column('phone', sa.String(20)),
        sa.Column('address_line1', sa.String(200)),
        sa.Column('address_line2', sa.String(200)),
        sa.Column('city', sa.String(100)),
        sa.Column('state', sa.String(100)),
        sa.Column('pincode', sa.String(10)),
        sa.Column('country', sa.String(100), default='India'),
        sa.Column('is_head_office', sa.Boolean, nullable=False, default=False),
        sa.Column('status', sa.String(20), nullable=False, default='ACTIVE'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('is_deleted', sa.Boolean, nullable=False, default=False)
    )

    # ─── Company Role ───────────────────────────────────────────────────────
    op.create_table(
        'company_role',
        sa.Column('role_id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('company.company_id'), nullable=False, index=True),
        sa.Column('role_name', sa.String(50), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('permissions', postgresql.JSONB, default={}),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )

    # ─── Company User ───────────────────────────────────────────────────────
    op.create_table(
        'company_user',
        sa.Column('company_user_id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('company.company_id'), nullable=False, index=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('user.user_id'), nullable=False, index=True),
        sa.Column('role_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('company_role.role_id'), nullable=False),
        sa.Column('branch_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('company_branch.branch_id')),
        sa.Column('status', sa.String(20), nullable=False, default='ACTIVE'),
        sa.Column('invited_at', sa.DateTime(timezone=True)),
        sa.Column('joined_at', sa.DateTime(timezone=True)),
        sa.Column('invite_token', sa.String(500)),
        sa.Column('invite_token_expires_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('is_deleted', sa.Boolean, nullable=False, default=False)
    )

    # ─── Company Client ─────────────────────────────────────────────────────
    op.create_table(
        'company_client',
        sa.Column('client_id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('company.company_id'), nullable=False, index=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('user.user_id')),
        sa.Column('client_name', sa.String(200), nullable=False, index=True),
        sa.Column('client_code', sa.String(20), nullable=False),
        sa.Column('email', sa.String(150)),
        sa.Column('phone', sa.String(20)),
        sa.Column('alternate_phone', sa.String(20)),
        sa.Column('whatsapp', sa.String(20)),
        sa.Column('address_line1', sa.String(200)),
        sa.Column('address_line2', sa.String(200)),
        sa.Column('city', sa.String(100)),
        sa.Column('state', sa.String(100)),
        sa.Column('pincode', sa.String(10)),
        sa.Column('country', sa.String(100), default='India'),
        sa.Column('pan', sa.String(10)),
        sa.Column('gstin', sa.String(15)),
        sa.Column('cin', sa.String(21)),
        sa.Column('client_type', sa.String(50)),
        sa.Column('status', sa.String(20), nullable=False, default='ACTIVE'),
        sa.Column('assigned_manager_id', sa.Integer, sa.ForeignKey('user.user_id')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('is_deleted', sa.Boolean, nullable=False, default=False)
    )


def downgrade():
    op.drop_table('company_client')
    op.drop_table('company_user')
    op.drop_table('company_role')
    op.drop_table('company_branch')
    op.drop_table('company')
