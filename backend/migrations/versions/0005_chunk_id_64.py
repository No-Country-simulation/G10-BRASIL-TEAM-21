"""Aumenta para 64 caracteres o identificador dos chunks.

Revision ID: 0005
Revises: 0004
Create Date: 2026-11-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "chunks",
        "chunk_id",
        existing_type=sa.String(length=50),
        type_=sa.String(length=64),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "chunks",
        "chunk_id",
        existing_type=sa.String(length=64),
        type_=sa.String(length=50),
        existing_nullable=False,
    )
