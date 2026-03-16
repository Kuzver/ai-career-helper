"""add password_hash to users

Revision ID: b1f2c3d4e5f6
Revises: a9d66a9a1bb4
Create Date: 2026-03-16
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "b1f2c3d4e5f6"
down_revision: Union[str, None] = "a9d66a9a1bb4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("password_hash", sa.String(500), nullable=True),
        schema="db_schema",
    )


def downgrade() -> None:
    op.drop_column("users", "password_hash", schema="db_schema")
