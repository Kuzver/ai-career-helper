"""add user_roadmaps table

Revision ID: g6e7f8g9h0i1
Revises: f5d6e7f8g9h0
Create Date: 2026-03-24
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "g6e7f8g9h0i1"
down_revision: Union[str, None] = "f5d6e7f8g9h0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "db_schema"


def upgrade() -> None:
    op.create_table(
        "user_roadmaps",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), sa.ForeignKey(f"{SCHEMA}.users.id"), nullable=False, unique=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("data_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_table("user_roadmaps", schema=SCHEMA)
