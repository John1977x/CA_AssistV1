"""initial auth tables

Revision ID: b39fbe1d565d
Revises: 004_billing
Create Date: 2026-04-26 17:56:44.183082

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import tables, column


# revision identifiers, used by Alembic.
revision: str = 'b39fbe1d565d'
down_revision: Union[str, None] = '004_billing'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Define table reference
    user_table = table(
        "user",
        column("user_id", Integer),
        column("tenant_id", Integer),
        column("role_id", Integer),
        column("first_name", String),
        column("last_name", String),
        column("email", String),
        column("password_hash", Text),
        column("is_owner", Boolean),
        column("status", String),
        column("created_at", DateTime),
    )

    # 🔐 Hash password
    password = "Admin@123"
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    # Insert admin (assuming tenant_id=1, role_id=1 exists)
    op.bulk_insert(
        user_table,
        [
            {
                "tenant_id": 1,
                "role_id": 1,
                "first_name": "Admin",
                "last_name": "User",
                "email": "admin@example.com",
                "password_hash": hashed_password,
                "is_owner": True,
                "status": "ACTIVE",
                "created_at": datetime.utcnow(),
            }
        ],
    )


def downgrade() -> None:
    op.execute("DELETE FROM \"user\" WHERE email='admin@example.com'")