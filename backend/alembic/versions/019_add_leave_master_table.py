"""Add leave_master table

Revision ID: 019_add_leave_master_table
Revises: 018_add_compliance_tables
Create Date: 2026-05-13
"""
from alembic import op
import sqlalchemy as sa

revision = '019_add_leave_master_table'
down_revision = '018_add_compliance_tables'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'leave_master',
        sa.Column('leave_master_id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenant.tenant_id'), nullable=False),
        sa.Column('leave_type', sa.String(100), nullable=False),
        sa.Column('entitled', sa.Integer(), nullable=False),
        sa.Column('calendar_year', sa.Integer(), nullable=False),
        sa.Column('calculation', sa.String(50), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_leave_master_tenant_id', 'leave_master', ['tenant_id'])
    op.create_index('ix_leave_master_calendar_year', 'leave_master', ['calendar_year'])


def downgrade():
    op.drop_index('ix_leave_master_calendar_year', 'leave_master')
    op.drop_index('ix_leave_master_tenant_id', 'leave_master')
    op.drop_table('leave_master')
