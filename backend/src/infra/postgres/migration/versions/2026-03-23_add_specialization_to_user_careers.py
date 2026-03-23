"""add specialization text to user_careers

Revision ID: f5d6e7f8g9h0
Revises: e4c5d6e7f8g9
Create Date: 2026-03-23
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "f5d6e7f8g9h0"
down_revision: Union[str, None] = "e4c5d6e7f8g9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "db_schema"


def upgrade() -> None:
    op.add_column(
        "user_careers",
        sa.Column("specialization", sa.String(100), nullable=True),
        schema=SCHEMA,
    )
    op.alter_column(
        "user_careers", "specialization_id",
        existing_type=sa.UUID(), nullable=True,
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_column("user_careers", "specialization", schema=SCHEMA)
    op.alter_column(
        "user_careers", "specialization_id",
        existing_type=sa.UUID(), nullable=False,
        schema=SCHEMA,
    )
