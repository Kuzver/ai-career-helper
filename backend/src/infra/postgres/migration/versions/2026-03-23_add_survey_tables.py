"""add survey tables

Revision ID: d3b4c5d6e7f8
Revises: c2a3b4d5e6f7
Create Date: 2026-03-23
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "d3b4c5d6e7f8"
down_revision: Union[str, None] = "c2a3b4d5e6f7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "db_schema"


def upgrade() -> None:
    op.create_table(
        "surveys",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_mandatory", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_by", sa.UUID(), sa.ForeignKey(f"{SCHEMA}.users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema=SCHEMA,
    )

    op.create_table(
        "survey_questions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("survey_id", sa.UUID(), sa.ForeignKey(f"{SCHEMA}.surveys.id", ondelete="CASCADE"), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("question_type", sa.String(50), nullable=False, server_default="single"),
        sa.Column("order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema=SCHEMA,
    )

    op.create_table(
        "survey_options",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("question_id", sa.UUID(), sa.ForeignKey(f"{SCHEMA}.survey_questions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("text", sa.String(500), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema=SCHEMA,
    )

    op.create_table(
        "survey_responses",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), sa.ForeignKey(f"{SCHEMA}.users.id"), nullable=False),
        sa.Column("survey_id", sa.UUID(), sa.ForeignKey(f"{SCHEMA}.surveys.id", ondelete="CASCADE"), nullable=False),
        sa.Column("is_validated", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("validation_result", sa.Text(), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema=SCHEMA,
    )

    op.create_table(
        "survey_answers",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("response_id", sa.UUID(), sa.ForeignKey(f"{SCHEMA}.survey_responses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("question_id", sa.UUID(), sa.ForeignKey(f"{SCHEMA}.survey_questions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("option_id", sa.UUID(), sa.ForeignKey(f"{SCHEMA}.survey_options.id", ondelete="SET NULL"), nullable=True),
        sa.Column("free_text", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_table("survey_answers", schema=SCHEMA)
    op.drop_table("survey_responses", schema=SCHEMA)
    op.drop_table("survey_options", schema=SCHEMA)
    op.drop_table("survey_questions", schema=SCHEMA)
    op.drop_table("surveys", schema=SCHEMA)
