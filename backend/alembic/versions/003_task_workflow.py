"""Add task, task_detail, task_reminder tables

Revision ID: 003_task_workflow
Revises: 002_customer_crm
Create Date: 2024-01-03 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "003_task_workflow"
down_revision: Union[str, None] = "002_customer_crm"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── task ─────────────────────────────────────────────────────────────────
    op.create_table(
        "task",
        sa.Column("task_id",               sa.Integer(),     autoincrement=True, nullable=False),
        sa.Column("tenant_id",             sa.Integer(),     nullable=False),
        sa.Column("customer_id",           sa.Integer(),     nullable=False),
        sa.Column("branch_id",             sa.Integer(),     nullable=True),
        sa.Column("assigned_to_user_id",   sa.Integer(),     nullable=True),
        sa.Column("reviewer_user_id",      sa.Integer(),     nullable=True),
        sa.Column("task_type_code",        sa.String(60),    nullable=False),
        sa.Column("task_title",            sa.String(300),   nullable=False),
        sa.Column("description",           sa.Text(),        nullable=True),
        sa.Column("financial_year",        sa.String(7),     nullable=True),
        sa.Column("return_period",         sa.String(20),    nullable=True),
        sa.Column("due_date",              sa.Date(),        nullable=False),
        sa.Column("internal_due_date",     sa.Date(),        nullable=True),
        sa.Column("priority",              sa.String(10),    nullable=False, server_default="MEDIUM"),
        sa.Column("status",                sa.String(30),    nullable=False, server_default="PENDING"),
        sa.Column("completion_percentage", sa.SmallInteger(),nullable=False, server_default="0"),
        sa.Column("billing_status",        sa.String(20),    nullable=False, server_default="UNBILLED"),
        sa.Column("billed_amount",         sa.Numeric(10, 2),nullable=True),
        sa.Column("estimated_hours",       sa.Numeric(6, 2), nullable=True),
        sa.Column("actual_hours",          sa.Numeric(6, 2), nullable=True),
        sa.Column("acknowledgement_number",sa.String(100),   nullable=True),
        sa.Column("filed_at",              sa.DateTime(timezone=True), nullable=True),
        sa.Column("filed_by_user_id",      sa.Integer(),     nullable=True),
        sa.Column("parent_task_id",        sa.Integer(),     nullable=True),
        sa.Column("tags",                  postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("is_deleted",            sa.Boolean(),     nullable=False, server_default=sa.false()),
        sa.ForeignKeyConstraint(["tenant_id"],           ["tenant.tenant_id"],   name="fk_task_tenant_id_tenant"),
        sa.ForeignKeyConstraint(["customer_id"],         ["customer.customer_id"], name="fk_task_customer_id_customer"),
        sa.ForeignKeyConstraint(["branch_id"],           ["branch.branch_id"],   name="fk_task_branch_id_branch"),
        sa.ForeignKeyConstraint(["assigned_to_user_id"], ["user.user_id"],       name="fk_task_assigned_to_user_id_user"),
        sa.ForeignKeyConstraint(["reviewer_user_id"],    ["user.user_id"],       name="fk_task_reviewer_user_id_user"),
        sa.ForeignKeyConstraint(["filed_by_user_id"],    ["user.user_id"],       name="fk_task_filed_by_user_id_user"),
        sa.ForeignKeyConstraint(["parent_task_id"],      ["task.task_id"],       name="fk_task_parent_task_id_task"),
        sa.PrimaryKeyConstraint("task_id", name="pk_task"),
    )
    op.create_index("ix_task_tenant_id",   "task", ["tenant_id"])
    op.create_index("ix_task_customer_id", "task", ["customer_id"])
    op.create_index("ix_task_status",      "task", ["status"])
    op.create_index("ix_task_due_date",    "task", ["due_date"])
    op.create_index("ix_task_priority",    "task", ["priority"])

    # ── task_detail ───────────────────────────────────────────────────────────
    op.create_table(
        "task_detail",
        sa.Column("task_detail_id",       sa.Integer(),  autoincrement=True, nullable=False),
        sa.Column("task_id",              sa.Integer(),  nullable=False),
        sa.Column("tenant_id",            sa.Integer(),  nullable=False),
        sa.Column("step_title",           sa.String(200),nullable=False),
        sa.Column("step_description",     sa.Text(),     nullable=True),
        sa.Column("step_order",           sa.Integer(),  nullable=False, server_default="0"),
        sa.Column("assigned_to_user_id",  sa.Integer(),  nullable=True),
        sa.Column("status",               sa.String(30), nullable=False, server_default="PENDING"),
        sa.Column("is_required",          sa.Boolean(),  nullable=False, server_default=sa.true()),
        sa.Column("is_client_action",     sa.Boolean(),  nullable=False, server_default=sa.false()),
        sa.Column("due_date",             sa.Date(),     nullable=True),
        sa.Column("completed_at",         sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_by_user_id", sa.Integer(),  nullable=True),
        sa.Column("attachments_json",     postgresql.JSONB(), nullable=True),
        sa.Column("notes_json",           postgresql.JSONB(), nullable=True),
        sa.Column("form_data_json",       postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["task_id"],              ["task.task_id"],   name="fk_task_detail_task_id_task"),
        sa.ForeignKeyConstraint(["tenant_id"],            ["tenant.tenant_id"], name="fk_task_detail_tenant_id_tenant"),
        sa.ForeignKeyConstraint(["assigned_to_user_id"],  ["user.user_id"],   name="fk_task_detail_assigned_to_user_id_user"),
        sa.ForeignKeyConstraint(["completed_by_user_id"], ["user.user_id"],   name="fk_task_detail_completed_by_user_id_user"),
        sa.PrimaryKeyConstraint("task_detail_id", name="pk_task_detail"),
    )
    op.create_index("ix_task_detail_task_id", "task_detail", ["task_id"])

    # ── task_reminder ─────────────────────────────────────────────────────────
    op.create_table(
        "task_reminder",
        sa.Column("reminder_id",         sa.Integer(),  autoincrement=True, nullable=False),
        sa.Column("tenant_id",           sa.Integer(),  nullable=False),
        sa.Column("task_id",             sa.Integer(),  nullable=False),
        sa.Column("reminder_type",       sa.String(20), nullable=False),
        sa.Column("target_user_id",      sa.Integer(),  nullable=True),
        sa.Column("target_customer_id",  sa.Integer(),  nullable=True),
        sa.Column("channel",             sa.String(20), nullable=False),
        sa.Column("subject",             sa.String(300),nullable=True),
        sa.Column("message_body",        sa.Text(),     nullable=False),
        sa.Column("template_code",       sa.String(60), nullable=True),
        sa.Column("scheduled_at",        sa.DateTime(timezone=True), nullable=False),
        sa.Column("sent_at",             sa.DateTime(timezone=True), nullable=True),
        sa.Column("delivery_status",     sa.String(20), nullable=False, server_default="PENDING"),
        sa.Column("delivery_error",      sa.Text(),     nullable=True),
        sa.Column("retry_count",         sa.Integer(),  nullable=False, server_default="0"),
        sa.Column("is_recurring",        sa.Boolean(),  nullable=False, server_default=sa.false()),
        sa.Column("recurrence_rule",     sa.String(100),nullable=True),
        sa.Column("is_acknowledged",     sa.Boolean(),  nullable=False, server_default=sa.false()),
        sa.Column("acknowledged_at",     sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by_user_id",  sa.Integer(),  nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["tenant_id"],          ["tenant.tenant_id"],    name="fk_task_reminder_tenant_id_tenant"),
        sa.ForeignKeyConstraint(["task_id"],            ["task.task_id"],        name="fk_task_reminder_task_id_task"),
        sa.ForeignKeyConstraint(["target_user_id"],     ["user.user_id"],        name="fk_task_reminder_target_user_id_user"),
        sa.ForeignKeyConstraint(["target_customer_id"], ["customer.customer_id"],name="fk_task_reminder_target_customer_id_customer"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["user.user_id"],        name="fk_task_reminder_created_by_user_id_user"),
        sa.PrimaryKeyConstraint("reminder_id", name="pk_task_reminder"),
    )
    op.create_index("ix_task_reminder_task_id",     "task_reminder", ["task_id"])
    op.create_index("ix_task_reminder_scheduled_at","task_reminder", ["scheduled_at"])


def downgrade() -> None:
    op.drop_table("task_reminder")
    op.drop_table("task_detail")
    op.drop_table("task")
