"""Add notification tables

Revision ID: 021_add_notifications
Revises: 020_add_leave_application_table
Create Date: 2026-05-18

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '021_add_notifications'
down_revision = '020_add_leave_application_table'
branch_labels = None
depends_on = None


def upgrade():
    # ─── Notification ────────────────────────────────────────────────────────
    op.create_table(
        'notification',
        sa.Column('notification_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('user.user_id'), nullable=False, index=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('notification_type', sa.String(50), nullable=False, default='info'),
        sa.Column('status', sa.String(20), nullable=False, default='unread'),
        sa.Column('related_entity_type', sa.String(50)),
        sa.Column('related_entity_id', sa.Integer),
        sa.Column('action_url', sa.String(500)),
        sa.Column('metadata', postgresql.JSONB, default={}),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('read_at', sa.DateTime(timezone=True)),
        sa.Column('archived_at', sa.DateTime(timezone=True)),
    )

    # ─── Notification Preference ────────────────────────────────────────────
    op.create_table(
        'notification_preference',
        sa.Column('preference_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('user.user_id'), nullable=False, unique=True, index=True),
        sa.Column('task_assigned', sa.Boolean, nullable=False, default=True),
        sa.Column('task_completed', sa.Boolean, nullable=False, default=True),
        sa.Column('document_request', sa.Boolean, nullable=False, default=True),
        sa.Column('assignment_submitted', sa.Boolean, nullable=False, default=True),
        sa.Column('ticket_created', sa.Boolean, nullable=False, default=True),
        sa.Column('ticket_updated', sa.Boolean, nullable=False, default=True),
        sa.Column('user_invited', sa.Boolean, nullable=False, default=True),
        sa.Column('company_created', sa.Boolean, nullable=False, default=True),
        sa.Column('subscription_updated', sa.Boolean, nullable=False, default=True),
        sa.Column('email_notifications', sa.Boolean, nullable=False, default=True),
        sa.Column('in_app_notifications', sa.Boolean, nullable=False, default=True),
        sa.Column('quiet_hours_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('quiet_hours_start', sa.String(5)),
        sa.Column('quiet_hours_end', sa.String(5)),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table('notification_preference')
    op.drop_table('notification')
