"""Add document request tickets table

Revision ID: 007_add_document_request_tickets
Revises: ad06b3af97a2
Create Date: 2026-05-07 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '007_add_document_request_tickets'
down_revision = 'ad06b3af97a2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create document_request_tickets table
    op.create_table(
        'document_request_tickets',
        sa.Column('ticket_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('client_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('requested_by_user_id', sa.Integer(), nullable=False),
        sa.Column('document_types', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('priority', sa.String(length=20), nullable=False, server_default='NORMAL'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='OPEN'),
        sa.Column('assigned_to_user_id', sa.Integer(), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_by_user_id', sa.Integer(), nullable=True),
        sa.Column('completion_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['company_id'], ['company.company_id'], ),
        sa.ForeignKeyConstraint(['client_id'], ['company_client.client_id'], ),
        sa.ForeignKeyConstraint(['requested_by_user_id'], ['user.user_id'], ),
        sa.ForeignKeyConstraint(['assigned_to_user_id'], ['user.user_id'], ),
        sa.ForeignKeyConstraint(['completed_by_user_id'], ['user.user_id'], ),
        sa.PrimaryKeyConstraint('ticket_id')
    )
    op.create_index(op.f('ix_document_request_tickets_company_id'), 'document_request_tickets', ['company_id'], unique=False)
    op.create_index(op.f('ix_document_request_tickets_client_id'), 'document_request_tickets', ['client_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_document_request_tickets_client_id'), table_name='document_request_tickets')
    op.drop_index(op.f('ix_document_request_tickets_company_id'), table_name='document_request_tickets')
    op.drop_table('document_request_tickets')
