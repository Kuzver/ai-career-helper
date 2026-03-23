"""add role to users, name to user_careers

Revision ID: c2a3b4d5e6f7
Revises: b1f2c3d4e5f6
Create Date: 2026-03-23
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "c2a3b4d5e6f7"
down_revision: Union[str, None] = "b1f2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("role", sa.String(50), nullable=False, server_default="user"),
        schema="db_schema",
    )
    op.add_column(
        "user_careers",
        sa.Column("name", sa.String(255), nullable=True),
        schema="db_schema",
    )


def downgrade() -> None:
    op.drop_column("user_careers", "name", schema="db_schema")
    op.drop_column("users", "role", schema="db_schema")
