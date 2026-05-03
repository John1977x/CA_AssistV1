"""initial auth tables

Revision ID: b39fbe1d565d
Revises: 004_billing
Create Date: 2026-04-26 17:56:44.183082

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import table, column, Integer, String, Text, DateTime, Boolean
import bcrypt
from datetime import datetime


# revision identifiers, used by Alembic.
revision: str = 'b39fbe1d565d'
down_revision: Union[str, None] = '004_billing'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # This migration is a merge point and doesn't create any new schema.
    # All schema changes are handled by the main migration branches.
    pass


def downgrade() -> None:
    # No-op for downgrade
    pass