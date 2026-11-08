"""Eventos de XP de upload e de erro em quiz.

- eventos_xp.adaptacao_id passa a aceitar nulo e ganha documento_id (evento de upload)
- novos tipos: upload_documento e erro_quiz (XP negativo)
- índices únicos: uma penalidade por pergunta e um XP de upload por documento

Revision ID: 0004
Revises: 0003
Create Date: 2026-11-02
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.alter_column(
        "eventos_xp", "adaptacao_id", existing_type=postgresql.UUID(as_uuid=True), nullable=True
    )
    op.add_column(
        "eventos_xp",
        sa.Column(
            "documento_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("documentos.documento_id", ondelete="CASCADE"),
            nullable=True,
        ),
    )
    op.drop_constraint("ck_eventos_tipo", "eventos_xp", type_="check")
    op.create_check_constraint(
        "ck_eventos_tipo",
        "eventos_xp",
        "tipo IN ('upload_documento','geracao_conteudo','acerto_quiz','erro_quiz')",
    )
    op.create_check_constraint(
        "ck_eventos_origem",
        "eventos_xp",
        "(tipo = 'upload_documento' AND documento_id IS NOT NULL) "
        "OR (tipo <> 'upload_documento' AND adaptacao_id IS NOT NULL)",
    )
    op.create_index(
        "ux_eventos_erro_quiz",
        "eventos_xp",
        ["adaptacao_id", "item_indice"],
        unique=True,
        postgresql_where=sa.text("tipo = 'erro_quiz'"),
    )
    op.create_index(
        "ux_eventos_upload",
        "eventos_xp",
        ["usuario_id", "documento_id"],
        unique=True,
        postgresql_where=sa.text("tipo = 'upload_documento'"),
    )


def downgrade() -> None:
    # Os eventos novos não cabem no esquema antigo: são descartados (o xp_total não é recalculado).
    op.execute("DELETE FROM eventos_xp WHERE tipo IN ('upload_documento','erro_quiz')")
    op.drop_index("ux_eventos_upload", table_name="eventos_xp")
    op.drop_index("ux_eventos_erro_quiz", table_name="eventos_xp")
    op.drop_constraint("ck_eventos_origem", "eventos_xp", type_="check")
    op.drop_constraint("ck_eventos_tipo", "eventos_xp", type_="check")
    op.create_check_constraint(
        "ck_eventos_tipo", "eventos_xp", "tipo IN ('geracao_conteudo','acerto_quiz')"
    )
    op.drop_column("eventos_xp", "documento_id")
    op.alter_column(
        "eventos_xp", "adaptacao_id", existing_type=postgresql.UUID(as_uuid=True), nullable=False
    )
