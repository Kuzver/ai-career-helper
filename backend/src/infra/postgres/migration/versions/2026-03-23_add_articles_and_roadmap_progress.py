"""add articles, article_categories, user_roadmap_progress

Revision ID: e4c5d6e7f8g9
Revises: d3b4c5d6e7f8
Create Date: 2026-03-23
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "e4c5d6e7f8g9"
down_revision: Union[str, None] = "d3b4c5d6e7f8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "db_schema"


def upgrade() -> None:
    op.create_table(
        "article_categories",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(255), nullable=False, unique=True),
        sa.Column("order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema=SCHEMA,
    )

    op.create_table(
        "articles",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("slug", sa.String(500), nullable=False, unique=True),
        sa.Column("content_md", sa.Text(), nullable=False),
        sa.Column("category_id", sa.UUID(), sa.ForeignKey(f"{SCHEMA}.article_categories.id", ondelete="SET NULL"), nullable=True),
        sa.Column("specialization", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema=SCHEMA,
    )

    op.create_table(
        "user_roadmap_progress",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), sa.ForeignKey(f"{SCHEMA}.users.id"), nullable=False),
        sa.Column("roadmap_key", sa.String(100), nullable=False),
        sa.Column("step_id", sa.String(100), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_table("user_roadmap_progress", schema=SCHEMA)
    op.drop_table("articles", schema=SCHEMA)
    op.drop_table("article_categories", schema=SCHEMA)
