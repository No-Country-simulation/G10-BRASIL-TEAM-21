"""inicial

Revision ID: 0001
Revises:
Create Date: 2026-10-21
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "usuarios",
        sa.Column("usuario_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("nome", sa.String(200), nullable=False),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("senha_hash", sa.String(255), nullable=False),
        sa.Column("nivel_declarado", sa.String(30), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint(
            "nivel_declarado IN ('Iniciante','Basico','Intermediario','Avancado','Especialista')",
            name="ck_usuarios_nivel",
        ),
    )
    op.execute("CREATE UNIQUE INDEX ux_usuarios_email_lower ON usuarios (lower(email))")

    op.create_table(
        "perfis_evolucao",
        sa.Column(
            "usuario_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("usuarios.usuario_id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("nivel_atual", sa.String(30), nullable=False),
        sa.Column("xp_total", sa.Integer, nullable=False, server_default="0"),
        sa.Column(
            "atualizado_em",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        sa.CheckConstraint("xp_total >= 0", name="ck_perfil_xp_nonneg"),
    )

    op.create_table(
        "documentos",
        sa.Column("documento_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "usuario_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("usuarios.usuario_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("titulo", sa.String(500), nullable=False),
        sa.Column("formato_origem", sa.String(20), nullable=False),
        sa.Column("objeto_oci", sa.String(1000), nullable=False, server_default=""),
        sa.Column("status_upload", sa.String(20), nullable=False, server_default="pendente"),
        sa.Column("hash_conteudo", sa.String(64), nullable=False),
        sa.Column("nivel_documento_estimado", sa.String(30), nullable=True),
        sa.Column("dominio_conhecimento", sa.String(30), nullable=True),
        sa.Column("classificador_usado", sa.String(20), nullable=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("usuario_id", "hash_conteudo", name="ux_documentos_usuario_hash"),
        sa.CheckConstraint(
            "status_upload IN ('pendente','concluido','falha')",
            name="ck_documentos_status",
        ),
        sa.CheckConstraint(
            "dominio_conhecimento IS NULL OR dominio_conhecimento IN "
            "('Geral','TI','Medicina','Financas','Juridico','Engenharia','Educacao')",
            name="ck_documentos_dominio",
        ),
        sa.CheckConstraint(
            "classificador_usado IS NULL OR classificador_usado IN ('local','api','fallback')",
            name="ck_documentos_classificador",
        ),
    )
    op.create_index("ix_documentos_usuario_criado", "documentos", ["usuario_id", "criado_em"])

    op.create_table(
        "chunks",
        sa.Column(
            "documento_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("documentos.documento_id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("chunk_id", sa.String(50), primary_key=True),
        sa.Column("ordem", sa.Integer, nullable=False),
        sa.Column("texto", sa.Text, nullable=False),
    )
    # tsvector gerado + índice GIN (RN-22)
    op.execute(
        "ALTER TABLE chunks ADD COLUMN tsvector_conteudo tsvector "
        "GENERATED ALWAYS AS (to_tsvector('portuguese', texto)) STORED"
    )
    op.execute("CREATE INDEX ix_chunks_tsvector ON chunks USING GIN (tsvector_conteudo)")

    op.create_table(
        "adaptacoes",
        sa.Column("adaptacao_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "usuario_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("usuarios.usuario_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "documento_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("documentos.documento_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("perfil_destinatario", sa.String(30), nullable=False),
        sa.Column("formato_saida", sa.String(30), nullable=False),
        sa.Column("nicho_setor", sa.String(30), nullable=False),
        sa.Column("nivel_detalhe", sa.String(30), nullable=False),
        sa.Column("nivel_do_usuario_no_momento", sa.String(30), nullable=False),
        sa.Column("cache_key", sa.String(64), nullable=False),
        sa.Column("resultado", postgresql.JSONB, nullable=False),
        sa.Column("ancoragem_fonte_score", sa.Numeric(4, 3), nullable=False),
        sa.Column("objeto_oci", sa.String(1000), nullable=False, server_default=""),
        sa.Column("status_upload", sa.String(20), nullable=False, server_default="pendente"),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint(
            "status_upload IN ('pendente','concluido','falha')",
            name="ck_adaptacoes_status",
        ),
    )
    op.create_index("ix_adaptacoes_usuario_criado", "adaptacoes", ["usuario_id", "criado_em"])
    op.create_index("ix_adaptacoes_documento", "adaptacoes", ["documento_id"])
    op.execute(
        "CREATE UNIQUE INDEX ux_adaptacoes_usuario_cache "
        "ON adaptacoes (usuario_id, cache_key) "
        "WHERE status_upload = 'concluido'"
    )

    op.create_table(
        "eventos_xp",
        sa.Column("evento_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "usuario_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("usuarios.usuario_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "adaptacao_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("adaptacoes.adaptacao_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("tipo", sa.String(30), nullable=False),
        sa.Column("xp", sa.Integer, nullable=False),
        sa.Column("item_indice", sa.Integer, nullable=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("tipo IN ('geracao_conteudo','acerto_quiz')", name="ck_eventos_tipo"),
    )
    op.execute(
        "CREATE UNIQUE INDEX ux_eventos_acerto_quiz "
        "ON eventos_xp (adaptacao_id, item_indice) "
        "WHERE tipo = 'acerto_quiz'"
    )

    op.create_table(
        "conceitos_progresso",
        sa.Column(
            "usuario_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("usuarios.usuario_id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("conceito", sa.String(200), primary_key=True),
        sa.Column("nivel_origem", sa.String(30), nullable=False),
        sa.Column("estado", sa.String(20), nullable=False, server_default="em_aprendizado"),
        sa.Column("acertos_quiz", sa.Integer, nullable=False, server_default="0"),
        sa.CheckConstraint("estado IN ('em_aprendizado','dominado')", name="ck_conceitos_estado"),
    )

    op.create_table(
        "testes_nivel",
        sa.Column("teste_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "usuario_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("usuarios.usuario_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("nivel_avaliado", sa.String(30), nullable=False),
        sa.Column("perguntas", postgresql.JSONB, nullable=False),
        sa.Column("respostas", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("percentual_dominio", sa.Numeric(4, 3), nullable=True),
        sa.Column("aprovado", sa.Boolean, nullable=True),
        sa.Column("tentativa", sa.Integer, nullable=False, server_default="1"),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_testes_usuario_criado", "testes_nivel", ["usuario_id", "criado_em"])


def downgrade() -> None:
    op.drop_table("testes_nivel")
    op.drop_table("conceitos_progresso")
    op.drop_table("eventos_xp")
    op.drop_table("adaptacoes")
    op.drop_table("chunks")
    op.drop_table("documentos")
    op.drop_table("perfis_evolucao")
    op.drop_table("usuarios")
    # Extensão vector fica (não removemos: pode ser compartilhada)
