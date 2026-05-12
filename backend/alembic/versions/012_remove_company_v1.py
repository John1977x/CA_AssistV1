"""Remove deprecated company v1 tables

Revision ID: 012_remove_company_v1
Revises: 011_add_register_table
Create Date: 2024-01-01 00:00:00.000000

This migration removes the deprecated v1 company model tables.
"""
from alembic import op
import sqlalchemy as sa

revision = '012_remove_company_v1'
down_revision = '011_add_register_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop deprecated v1 company tables using raw SQL
    op.execute('DROP TABLE IF EXISTS client_documents CASCADE')
    op.execute('DROP TABLE IF EXISTS customer_companies CASCADE')
    op.execute('DROP TABLE IF EXISTS tenant_companies CASCADE')


def downgrade() -> None:
    pass
