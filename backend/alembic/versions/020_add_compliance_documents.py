"""Add compliance document tables

Revision ID: 020_add_compliance_documents
Revises: 019_add_notifications
Create Date: 2026-05-18

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '020_add_compliance_documents'
down_revision = '019_add_notifications'
branch_labels = None
depends_on = None


def upgrade():
    # ─── Compliance Document ────────────────────────────────────────────────
    op.create_table(
        'compliance_document',
        sa.Column('document_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('compliance_id', sa.Integer, sa.ForeignKey('compliance.compliance_id'), nullable=False, index=True),
        sa.Column('document_type', sa.String(50), nullable=False, index=True),
        sa.Column('document_name', sa.String(200), nullable=False),
        sa.Column('document_number', sa.String(100)),
        sa.Column('file_url', sa.Text, nullable=False),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('file_size', sa.Integer),
        sa.Column('file_type', sa.String(50)),
        sa.Column('username', sa.String(200)),
        sa.Column('password_hash', sa.Text),
        sa.Column('access_url', sa.Text),
        sa.Column('issue_date', sa.Date),
        sa.Column('expiry_date', sa.Date),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
        sa.Column('status', sa.String(20), nullable=False, default='pending'),
        sa.Column('verified_by_user_id', sa.Integer, sa.ForeignKey('user.user_id')),
        sa.Column('verified_at', sa.DateTime(timezone=True)),
        sa.Column('verification_notes', sa.Text),
        sa.Column('description', sa.Text),
        sa.Column('metadata', postgresql.JSONB, default={}),
        sa.Column('uploaded_by_user_id', sa.Integer, sa.ForeignKey('user.user_id'), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_by_user_id', sa.Integer, sa.ForeignKey('user.user_id')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('is_deleted', sa.Boolean, nullable=False, default=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.Column('deleted_by_user_id', sa.Integer, sa.ForeignKey('user.user_id')),
    )

    # ─── Client Uploaded Document ───────────────────────────────────────────
    op.create_table(
        'client_uploaded_document',
        sa.Column('upload_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('compliance_id', sa.Integer, sa.ForeignKey('compliance.compliance_id'), nullable=False, index=True),
        sa.Column('client_id', sa.Integer, sa.ForeignKey('customer.customer_id'), nullable=False, index=True),
        sa.Column('document_type', sa.String(50), nullable=False),
        sa.Column('document_name', sa.String(200), nullable=False),
        sa.Column('document_number', sa.String(100)),
        sa.Column('file_url', sa.Text, nullable=False),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('file_size', sa.Integer),
        sa.Column('file_type', sa.String(50)),
        sa.Column('username', sa.String(200)),
        sa.Column('password_hash', sa.Text),
        sa.Column('access_url', sa.Text),
        sa.Column('issue_date', sa.Date),
        sa.Column('expiry_date', sa.Date),
        sa.Column('status', sa.String(20), nullable=False, default='pending'),
        sa.Column('verified_by_user_id', sa.Integer, sa.ForeignKey('user.user_id')),
        sa.Column('verified_at', sa.DateTime(timezone=True)),
        sa.Column('verification_notes', sa.Text),
        sa.Column('rejection_reason', sa.Text),
        sa.Column('description', sa.Text),
        sa.Column('metadata', postgresql.JSONB, default={}),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('is_deleted', sa.Boolean, nullable=False, default=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
    )

    # ─── Document Template ──────────────────────────────────────────────────
    op.create_table(
        'document_template',
        sa.Column('template_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('document_type', sa.String(50), nullable=False, unique=True),
        sa.Column('display_name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('is_mandatory', sa.Boolean, nullable=False, default=False),
        sa.Column('is_recurring', sa.Boolean, nullable=False, default=False),
        sa.Column('renewal_frequency', sa.String(50)),
        sa.Column('accepted_file_types', sa.String(200)),
        sa.Column('max_file_size', sa.Integer),
        sa.Column('metadata', postgresql.JSONB, default={}),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table('document_template')
    op.drop_table('client_uploaded_document')
    op.drop_table('compliance_document')
