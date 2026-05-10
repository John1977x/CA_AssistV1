"""Add assignments module

Revision ID: 008_add_assignments
Revises: 007_add_document_request_tickets
Create Date: 2026-05-10 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '008_add_assignments'
down_revision = '007_add_document_request_tickets'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create assignment_template table
    op.create_table(
        'assignment_template',
        sa.Column('template_id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('total_steps', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('estimated_hours', sa.Numeric(6, 2), nullable=True),
        sa.Column('difficulty_level', sa.String(20), nullable=False, server_default='MEDIUM'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenant.tenant_id'], ),
        sa.PrimaryKeyConstraint('template_id')
    )
    op.create_index(op.f('ix_assignment_template_tenant_id'), 'assignment_template', ['tenant_id'], unique=False)

    # Create assignment_template_step table
    op.create_table(
        'assignment_template_step',
        sa.Column('step_id', sa.Integer(), nullable=False),
        sa.Column('template_id', sa.Integer(), nullable=False),
        sa.Column('step_number', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('instructions', sa.Text(), nullable=True),
        sa.Column('estimated_hours', sa.Numeric(6, 2), nullable=True),
        sa.Column('is_required', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['template_id'], ['assignment_template.template_id'], ),
        sa.PrimaryKeyConstraint('step_id')
    )
    op.create_index(op.f('ix_assignment_template_step_template_id'), 'assignment_template_step', ['template_id'], unique=False)

    # Create assignment table
    op.create_table(
        'assignment',
        sa.Column('assignment_id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('template_id', sa.Integer(), nullable=False),
        sa.Column('assigned_to_user_id', sa.Integer(), nullable=False),
        sa.Column('assigned_by_user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(30), nullable=False, server_default='ASSIGNED'),
        sa.Column('completion_percentage', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_score', sa.Numeric(5, 2), nullable=True),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('approved_by_user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['assigned_by_user_id'], ['user.user_id'], ),
        sa.ForeignKeyConstraint(['assigned_to_user_id'], ['user.user_id'], ),
        sa.ForeignKeyConstraint(['approved_by_user_id'], ['user.user_id'], ),
        sa.ForeignKeyConstraint(['template_id'], ['assignment_template.template_id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenant.tenant_id'], ),
        sa.PrimaryKeyConstraint('assignment_id')
    )
    op.create_index(op.f('ix_assignment_tenant_id'), 'assignment', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_assignment_assigned_to_user_id'), 'assignment', ['assigned_to_user_id'], unique=False)
    op.create_index(op.f('ix_assignment_status'), 'assignment', ['status'], unique=False)

    # Create assignment_step_submission table
    op.create_table(
        'assignment_step_submission',
        sa.Column('submission_id', sa.Integer(), nullable=False),
        sa.Column('assignment_id', sa.Integer(), nullable=False),
        sa.Column('step_id', sa.Integer(), nullable=False),
        sa.Column('submitted_by_user_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(30), nullable=False, server_default='PENDING'),
        sa.Column('submission_text', sa.Text(), nullable=True),
        sa.Column('file_url', sa.String(500), nullable=True),
        sa.Column('file_name', sa.String(200), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('mime_type', sa.String(100), nullable=True),
        sa.Column('score', sa.Numeric(5, 2), nullable=True),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('reviewed_by_user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['assignment_id'], ['assignment.assignment_id'], ),
        sa.ForeignKeyConstraint(['reviewed_by_user_id'], ['user.user_id'], ),
        sa.ForeignKeyConstraint(['step_id'], ['assignment_template_step.step_id'], ),
        sa.ForeignKeyConstraint(['submitted_by_user_id'], ['user.user_id'], ),
        sa.PrimaryKeyConstraint('submission_id')
    )
    op.create_index(op.f('ix_assignment_step_submission_assignment_id'), 'assignment_step_submission', ['assignment_id'], unique=False)
    op.create_index(op.f('ix_assignment_step_submission_status'), 'assignment_step_submission', ['status'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_assignment_step_submission_status'), table_name='assignment_step_submission')
    op.drop_index(op.f('ix_assignment_step_submission_assignment_id'), table_name='assignment_step_submission')
    op.drop_table('assignment_step_submission')
    op.drop_index(op.f('ix_assignment_status'), table_name='assignment')
    op.drop_index(op.f('ix_assignment_assigned_to_user_id'), table_name='assignment')
    op.drop_index(op.f('ix_assignment_tenant_id'), table_name='assignment')
    op.drop_table('assignment')
    op.drop_index(op.f('ix_assignment_template_step_template_id'), table_name='assignment_template_step')
    op.drop_table('assignment_template_step')
    op.drop_index(op.f('ix_assignment_template_tenant_id'), table_name='assignment_template')
    op.drop_table('assignment_template')
