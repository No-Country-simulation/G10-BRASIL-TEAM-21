"""Armazena o tamanho original do arquivo enviado.

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-27
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.add_column(
        "documentos",
        sa.Column("tamanho_bytes", sa.Integer(), nullable=False, server_default="0"),
    )
    op.alter_column("documentos", "tamanho_bytes", server_default=None)


def downgrade() -> None:
    op.drop_column("documentos", "tamanho_bytes")
