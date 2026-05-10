"""Add ticket system tables

Revision ID: 009_add_tickets
Revises: 008_add_assignments
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '009_add_tickets'
down_revision = '008_add_assignments'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create ticket table
    op.create_table(
        'ticket',
        sa.Column('ticket_id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('raised_by_user_id', sa.Integer(), nullable=False),
        sa.Column('assigned_to_user_id', sa.Integer(), nullable=True),
        sa.Column('ticket_number', sa.String(50), nullable=False),
        sa.Column('title', sa.String(300), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('priority', sa.String(20), nullable=False, server_default='MEDIUM'),
        sa.Column('status', sa.String(30), nullable=False, server_default='OPEN'),
        sa.Column('resolution', sa.Text(), nullable=True),
        sa.Column('attachments_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('closed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolved_by_user_id', sa.Integer(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenant.tenant_id'], ),
        sa.ForeignKeyConstraint(['customer_id'], ['customer.customer_id'], ),
        sa.ForeignKeyConstraint(['raised_by_user_id'], ['user.user_id'], ),
        sa.ForeignKeyConstraint(['assigned_to_user_id'], ['user.user_id'], ),
        sa.ForeignKeyConstraint(['resolved_by_user_id'], ['user.user_id'], ),
        sa.PrimaryKeyConstraint('ticket_id'),
        sa.UniqueConstraint('ticket_number'),
    )

    # Create ticket_comment table
    op.create_table(
        'ticket_comment',
        sa.Column('comment_id', sa.Integer(), nullable=False),
        sa.Column('ticket_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('comment_text', sa.Text(), nullable=False),
        sa.Column('attachments_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_internal', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['ticket_id'], ['ticket.ticket_id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.user_id'], ),
        sa.PrimaryKeyConstraint('comment_id'),
    )

    # Create indexes
    op.create_index('ix_ticket_tenant_id', 'ticket', ['tenant_id'])
    op.create_index('ix_ticket_customer_id', 'ticket', ['customer_id'])
    op.create_index('ix_ticket_status', 'ticket', ['status'])
    op.create_index('ix_ticket_priority', 'ticket', ['priority'])
    op.create_index('ix_ticket_created_at', 'ticket', ['created_at'])
    op.create_index('ix_ticket_comment_ticket_id', 'ticket_comment', ['ticket_id'])


def downgrade() -> None:
    op.drop_index('ix_ticket_comment_ticket_id', table_name='ticket_comment')
    op.drop_index('ix_ticket_created_at', table_name='ticket')
    op.drop_index('ix_ticket_priority', table_name='ticket')
    op.drop_index('ix_ticket_status', table_name='ticket')
    op.drop_index('ix_ticket_customer_id', table_name='ticket')
    op.drop_index('ix_ticket_tenant_id', table_name='ticket')
    op.drop_table('ticket_comment')
    op.drop_table('ticket')
