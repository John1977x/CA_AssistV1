"""Add inward/outward register table

Revision ID: 011_add_register_table
Revises: 010_add_reset_token_columns
Create Date: 2026-05-12 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '011_add_register_table'
down_revision = '010_add_reset_token_columns'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'register',
        sa.Column('register_id',     sa.Integer(),                        nullable=False, autoincrement=True),
        sa.Column('tenant_id',       sa.Integer(),                        nullable=False),
        sa.Column('in_out_ward',     sa.String(10),                       nullable=False),
        sa.Column('doc_date',        sa.Date(),                           nullable=False),
        sa.Column('doc_type',        sa.String(60),                       nullable=False),
        sa.Column('doc_description', sa.Text(),                           nullable=False),
        sa.Column('client_id',       sa.Integer(),                        nullable=True),
        sa.Column('owner_id',        sa.Integer(),                        nullable=True),
        sa.Column('employee_id',     sa.Integer(),                        nullable=True),
        sa.Column('sent_date',       sa.Date(),                           nullable=True),
        sa.Column('acknowledgement', sa.String(200),                      nullable=True),
        sa.Column('created_at',      sa.DateTime(timezone=True),          nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at',      sa.DateTime(timezone=True),          nullable=False, server_default=sa.func.now()),
        sa.Column('is_deleted',      sa.Boolean(),                        nullable=False, server_default='false'),
        sa.PrimaryKeyConstraint('register_id', name='pk_register'),
        sa.ForeignKeyConstraint(['tenant_id'],   ['tenant.tenant_id'],    name='fk_register_tenant_id_tenant'),
        sa.ForeignKeyConstraint(['client_id'],   ['customer.customer_id'], name='fk_register_client_id_customer'),
        sa.ForeignKeyConstraint(['owner_id'],    ['user.user_id'],        name='fk_register_owner_id_user'),
        sa.ForeignKeyConstraint(['employee_id'], ['user.user_id'],        name='fk_register_employee_id_user'),
    )
    op.create_index('ix_register_tenant_id',   'register', ['tenant_id'])
    op.create_index('ix_register_doc_date',    'register', ['doc_date'])
    op.create_index('ix_register_in_out_ward', 'register', ['in_out_ward'])


def downgrade() -> None:
    op.drop_index('ix_register_in_out_ward', table_name='register')
    op.drop_index('ix_register_doc_date',    table_name='register')
    op.drop_index('ix_register_tenant_id',   table_name='register')
    op.drop_table('register')
