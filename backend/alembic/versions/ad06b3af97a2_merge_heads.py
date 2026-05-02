"""merge heads

Revision ID: ad06b3af97a2
Revises: 006_add_company, b39fbe1d565d
Create Date: 2026-05-02 17:04:23.721835

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ad06b3af97a2'
down_revision: Union[str, None] = ('006_add_company', 'b39fbe1d565d')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
