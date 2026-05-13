"""Add leave_application table

Revision ID: 020_add_leave_application_table
Revises: 019_add_leave_master_table
Create Date: 2026-05-13
"""
from alembic import op
import sqlalchemy as sa

revision = '020_add_leave_application_table'
down_revision = '019_add_leave_master_table'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'leave_application',
        sa.Column('leave_application_id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenant.tenant_id'), nullable=False),
        sa.Column('employee_id', sa.Integer(), sa.ForeignKey('user.user_id'), nullable=False),
        sa.Column('leave_type', sa.String(100), nullable=False),
        sa.Column('leave_date', sa.Date(), nullable=False),
        sa.Column('from_date', sa.Date(), nullable=False),
        sa.Column('to_date', sa.Date(), nullable=False),
        sa.Column('reason', sa.Text()),
        sa.Column('attachment_url', sa.String(500)),
        sa.Column('approver_id', sa.Integer(), sa.ForeignKey('user.user_id')),
        sa.Column('status', sa.String(20), nullable=False, server_default='PENDING'),
        sa.Column('approval_notes', sa.Text()),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_leave_application_tenant_id', 'leave_application', ['tenant_id'])
    op.create_index('ix_leave_application_employee_id', 'leave_application', ['employee_id'])
    op.create_index('ix_leave_application_status', 'leave_application', ['status'])


def downgrade():
    op.drop_index('ix_leave_application_status', 'leave_application')
    op.drop_index('ix_leave_application_employee_id', 'leave_application')
    op.drop_index('ix_leave_application_tenant_id', 'leave_application')
    op.drop_table('leave_application')
