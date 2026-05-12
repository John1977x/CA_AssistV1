"""Add reset_token and reset_expiry columns to user table

Revision ID: 010_add_reset_token_columns
Revises: 009_add_tickets
Create Date: 2026-05-12 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '010_add_reset_token_columns'
down_revision = '009_add_tickets'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('user', sa.Column('reset_token', sa.String(100), nullable=True))
    op.add_column('user', sa.Column('reset_expiry', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('user', 'reset_expiry')
    op.drop_column('user', 'reset_token')
