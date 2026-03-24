"""add is_required to survey_questions

Revision ID: h7f8g9h0i1j2
Revises: g6e7f8g9h0i1
Create Date: 2026-03-24
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "h7f8g9h0i1j2"
down_revision: Union[str, None] = "g6e7f8g9h0i1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "survey_questions",
        sa.Column("is_required", sa.Boolean(), nullable=False, server_default="true"),
        schema="db_schema",
    )


def downgrade() -> None:
    op.drop_column("survey_questions", "is_required", schema="db_schema")
