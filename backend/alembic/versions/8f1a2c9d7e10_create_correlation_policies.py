"""create correlation policies

Revision ID: 8f1a2c9d7e10
Revises: 976a36ece8a5
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8f1a2c9d7e10"
down_revision: Union[str, Sequence[str], None] = "976a36ece8a5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "correlation_policies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("condition", sa.JSON(), nullable=False),
        sa.Column("time_window_minutes", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(
        op.f("ix_correlation_policies_id"),
        "correlation_policies",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_correlation_policies_id"),
        table_name="correlation_policies",
    )
    op.drop_table("correlation_policies")
