"""Add compliance tracking tables

Revision ID: 018_add_compliance_tables
Revises: 013_comprehensive_uuid_migration
Create Date: 2024-01-01 00:00:00.000000

This migration adds compliance tracking tables:
- compliance: Store compliance records for clients/candidates
- compliance_task: Link compliance to tasks and track assignments
- compliance_history: Audit trail for compliance changes
- compliance_reminder: Reminders for compliance deadlines

NOTE: Using Integer IDs for now since the database hasn't been fully migrated to UUID yet.
These will be converted to UUID in a future migration.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, ARRAY

revision = '018_add_compliance_tables'
down_revision = '013_comprehensive_uuid_migration'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create compliance table
    op.create_table(
        'compliance',
        sa.Column('compliance_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('tenant_id', sa.Integer, nullable=False),
        sa.Column('customer_id', sa.Integer, nullable=False),
        sa.Column('compliance_type', sa.String(50), nullable=False),
        sa.Column('compliance_code', sa.String(30), nullable=False),
        sa.Column('pan', sa.String(10)),
        sa.Column('tan', sa.String(10)),
        sa.Column('gstin', sa.String(15)),
        sa.Column('gst_registration_type', sa.String(30)),
        sa.Column('gst_registration_date', sa.Date()),
        sa.Column('gst_cancellation_date', sa.Date()),
        sa.Column('tds_deductor_type', sa.String(50)),
        sa.Column('tds_circle_code', sa.String(20)),
        sa.Column('cin', sa.String(21)),
        sa.Column('company_registration_date', sa.Date()),
        sa.Column('financial_year', sa.String(7)),
        sa.Column('financial_year_start', sa.Integer()),
        sa.Column('financial_year_end', sa.Integer()),
        sa.Column('status', sa.String(30), nullable=False, server_default='ACTIVE'),
        sa.Column('compliance_status', sa.String(30), nullable=False, server_default='PENDING'),
        sa.Column('last_filing_date', sa.Date()),
        sa.Column('next_filing_date', sa.Date()),
        sa.Column('filing_frequency', sa.String(20)),
        sa.Column('registration_number', sa.String(100)),
        sa.Column('registration_certificate_url', sa.Text()),
        sa.Column('documents_json', JSONB()),
        sa.Column('contact_person_name', sa.String(200)),
        sa.Column('contact_person_email', sa.String(150)),
        sa.Column('contact_person_phone', sa.String(15)),
        sa.Column('registered_address', sa.Text()),
        sa.Column('notes', sa.Text()),
        sa.Column('custom_fields_json', JSONB()),
        sa.Column('created_by_user_id', sa.Integer),
        sa.Column('updated_by_user_id', sa.Integer),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenant.tenant_id'], ),
        sa.ForeignKeyConstraint(['customer_id'], ['customer.customer_id'], ),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['user.user_id'], ),
        sa.ForeignKeyConstraint(['updated_by_user_id'], ['user.user_id'], ),
    )
    op.create_index(op.f('ix_compliance_tenant_id'), 'compliance', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_compliance_customer_id'), 'compliance', ['customer_id'], unique=False)
    op.create_index(op.f('ix_compliance_compliance_type'), 'compliance', ['compliance_type'], unique=False)
    op.create_index(op.f('ix_compliance_status'), 'compliance', ['status'], unique=False)

    # Create compliance_task table
    op.create_table(
        'compliance_task',
        sa.Column('compliance_task_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('compliance_id', sa.Integer, nullable=False),
        sa.Column('task_id', sa.Integer, nullable=False),
        sa.Column('tenant_id', sa.Integer, nullable=False),
        sa.Column('assigned_to_user_id', sa.Integer, nullable=False),
        sa.Column('assigned_by_user_id', sa.Integer),
        sa.Column('task_type', sa.String(60), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('assigned_date', sa.Date(), nullable=False, server_default=sa.func.current_date()),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('completed_date', sa.Date()),
        sa.Column('status', sa.String(30), nullable=False, server_default='ASSIGNED'),
        sa.Column('completion_percentage', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('compliance_requirement', sa.String(200)),
        sa.Column('documents_required', ARRAY(sa.String())),
        sa.Column('documents_submitted_json', JSONB()),
        sa.Column('reviewed_by_user_id', sa.Integer),
        sa.Column('reviewed_date', sa.Date()),
        sa.Column('review_comments', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.ForeignKeyConstraint(['compliance_id'], ['compliance.compliance_id'], ),
        sa.ForeignKeyConstraint(['task_id'], ['task.task_id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenant.tenant_id'], ),
        sa.ForeignKeyConstraint(['assigned_to_user_id'], ['user.user_id'], ),
        sa.ForeignKeyConstraint(['assigned_by_user_id'], ['user.user_id'], ),
        sa.ForeignKeyConstraint(['reviewed_by_user_id'], ['user.user_id'], ),
    )
    op.create_index(op.f('ix_compliance_task_compliance_id'), 'compliance_task', ['compliance_id'], unique=False)
    op.create_index(op.f('ix_compliance_task_task_id'), 'compliance_task', ['task_id'], unique=False)
    op.create_index(op.f('ix_compliance_task_tenant_id'), 'compliance_task', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_compliance_task_assigned_to_user_id'), 'compliance_task', ['assigned_to_user_id'], unique=False)
    op.create_index(op.f('ix_compliance_task_status'), 'compliance_task', ['status'], unique=False)

    # Create compliance_history table
    op.create_table(
        'compliance_history',
        sa.Column('history_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('compliance_id', sa.Integer, nullable=False),
        sa.Column('tenant_id', sa.Integer, nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('field_name', sa.String(100)),
        sa.Column('old_value', sa.Text()),
        sa.Column('new_value', sa.Text()),
        sa.Column('changed_by_user_id', sa.Integer),
        sa.Column('change_reason', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['compliance_id'], ['compliance.compliance_id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenant.tenant_id'], ),
        sa.ForeignKeyConstraint(['changed_by_user_id'], ['user.user_id'], ),
    )
    op.create_index(op.f('ix_compliance_history_compliance_id'), 'compliance_history', ['compliance_id'], unique=False)
    op.create_index(op.f('ix_compliance_history_tenant_id'), 'compliance_history', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_compliance_history_action'), 'compliance_history', ['action'], unique=False)

    # Create compliance_reminder table
    op.create_table(
        'compliance_reminder',
        sa.Column('reminder_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('compliance_id', sa.Integer, nullable=False),
        sa.Column('tenant_id', sa.Integer, nullable=False),
        sa.Column('reminder_type', sa.String(30), nullable=False),
        sa.Column('reminder_date', sa.Date(), nullable=False),
        sa.Column('days_before_due', sa.Integer()),
        sa.Column('notify_user_ids', ARRAY(sa.String())),
        sa.Column('notification_channels', ARRAY(sa.String())),
        sa.Column('status', sa.String(20), nullable=False, server_default='PENDING'),
        sa.Column('sent_at', sa.DateTime(timezone=True)),
        sa.Column('acknowledged_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['compliance_id'], ['compliance.compliance_id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenant.tenant_id'], ),
    )
    op.create_index(op.f('ix_compliance_reminder_compliance_id'), 'compliance_reminder', ['compliance_id'], unique=False)
    op.create_index(op.f('ix_compliance_reminder_tenant_id'), 'compliance_reminder', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_compliance_reminder_reminder_type'), 'compliance_reminder', ['reminder_type'], unique=False)
    op.create_index(op.f('ix_compliance_reminder_status'), 'compliance_reminder', ['status'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_compliance_reminder_status'), table_name='compliance_reminder')
    op.drop_index(op.f('ix_compliance_reminder_reminder_type'), table_name='compliance_reminder')
    op.drop_index(op.f('ix_compliance_reminder_tenant_id'), table_name='compliance_reminder')
    op.drop_index(op.f('ix_compliance_reminder_compliance_id'), table_name='compliance_reminder')
    op.drop_table('compliance_reminder')
    op.drop_index(op.f('ix_compliance_history_action'), table_name='compliance_history')
    op.drop_index(op.f('ix_compliance_history_tenant_id'), table_name='compliance_history')
    op.drop_index(op.f('ix_compliance_history_compliance_id'), table_name='compliance_history')
    op.drop_table('compliance_history')
    op.drop_index(op.f('ix_compliance_task_status'), table_name='compliance_task')
    op.drop_index(op.f('ix_compliance_task_assigned_to_user_id'), table_name='compliance_task')
    op.drop_index(op.f('ix_compliance_task_tenant_id'), table_name='compliance_task')
    op.drop_index(op.f('ix_compliance_task_task_id'), table_name='compliance_task')
    op.drop_index(op.f('ix_compliance_task_compliance_id'), table_name='compliance_task')
    op.drop_table('compliance_task')
    op.drop_index(op.f('ix_compliance_status'), table_name='compliance')
    op.drop_index(op.f('ix_compliance_compliance_type'), table_name='compliance')
    op.drop_index(op.f('ix_compliance_customer_id'), table_name='compliance')
    op.drop_index(op.f('ix_compliance_tenant_id'), table_name='compliance')
    op.drop_table('compliance')
