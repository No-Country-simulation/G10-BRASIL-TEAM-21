"""Modelos SQLAlchemy 2.x. Embedding fica de fora até T2.9 (N indefinido)."""

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Computed,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


def _uuid() -> uuid.UUID:
    return uuid.uuid4()


class Usuario(Base):
    __tablename__ = "usuarios"
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_uuid
    )
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    nivel_declarado: Mapped[str] = mapped_column(String(30), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "nivel_declarado IN ('Iniciante','Basico','Intermediario','Avancado','Especialista')",
            name="ck_usuarios_nivel",
        ),
        Index("ux_usuarios_email_lower", func.lower(email), unique=True),
    )


class PerfilEvolucao(Base):
    __tablename__ = "perfis_evolucao"
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.usuario_id", ondelete="CASCADE"), primary_key=True
    )
    nivel_atual: Mapped[str] = mapped_column(String(30), nullable=False)
    xp_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (CheckConstraint("xp_total >= 0", name="ck_perfil_xp_nonneg"),)


class Documento(Base):
    __tablename__ = "documentos"
    documento_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_uuid
    )
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.usuario_id", ondelete="CASCADE"), nullable=False
    )
    titulo: Mapped[str] = mapped_column(String(500), nullable=False)
    formato_origem: Mapped[str] = mapped_column(String(20), nullable=False)
    objeto_oci: Mapped[str] = mapped_column(String(1000), nullable=False, default="")
    status_upload: Mapped[str] = mapped_column(String(20), nullable=False, default="pendente")
    hash_conteudo: Mapped[str] = mapped_column(String(64), nullable=False)
    tamanho_bytes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    nivel_documento_estimado: Mapped[str | None] = mapped_column(String(30), nullable=True)
    dominio_conhecimento: Mapped[str | None] = mapped_column(String(30), nullable=True)
    classificador_usado: Mapped[str | None] = mapped_column(String(20), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    chunks: Mapped[list["Chunk"]] = relationship(
        back_populates="documento", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("usuario_id", "hash_conteudo", name="ux_documentos_usuario_hash"),
        CheckConstraint(
            "status_upload IN ('pendente','concluido','falha')",
            name="ck_documentos_status",
        ),
        CheckConstraint(
            "dominio_conhecimento IS NULL OR dominio_conhecimento IN "
            "('Geral','TI','Medicina','Financas','Juridico','Engenharia','Educacao')",
            name="ck_documentos_dominio",
        ),
        CheckConstraint(
            "classificador_usado IS NULL OR classificador_usado IN ('local','api','fallback')",
            name="ck_documentos_classificador",
        ),
        Index("ix_documentos_usuario_criado", "usuario_id", "criado_em"),
    )


class Chunk(Base):
    __tablename__ = "chunks"
    documento_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documentos.documento_id", ondelete="CASCADE"),
        primary_key=True,
    )
    chunk_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    ordem: Mapped[int] = mapped_column(Integer, nullable=False)
    texto: Mapped[str] = mapped_column(Text, nullable=False)
    # tsvector gerado (para busca híbrida, RN-22). Sem embedding até T2.9.
    tsvector_conteudo: Mapped[str | None] = mapped_column(
        TSVECTOR,
        Computed("to_tsvector('portuguese', texto)", persisted=True),
        nullable=True,
    )

    documento: Mapped[Documento] = relationship(back_populates="chunks")

    __table_args__ = (Index("ix_chunks_tsvector", "tsvector_conteudo", postgresql_using="gin"),)


class Adaptacao(Base):
    __tablename__ = "adaptacoes"
    adaptacao_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_uuid
    )
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.usuario_id", ondelete="CASCADE"), nullable=False
    )
    documento_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documentos.documento_id", ondelete="CASCADE"),
        nullable=False,
    )
    perfil_destinatario: Mapped[str] = mapped_column(String(30), nullable=False)
    formato_saida: Mapped[str] = mapped_column(String(30), nullable=False)
    nicho_setor: Mapped[str] = mapped_column(String(30), nullable=False)
    nivel_detalhe: Mapped[str] = mapped_column(String(30), nullable=False)
    nivel_do_usuario_no_momento: Mapped[str] = mapped_column(String(30), nullable=False)
    cache_key: Mapped[str] = mapped_column(String(64), nullable=False)
    resultado: Mapped[dict] = mapped_column(JSONB, nullable=False)
    ancoragem_fonte_score: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)
    objeto_oci: Mapped[str] = mapped_column(String(1000), nullable=False, default="")
    status_upload: Mapped[str] = mapped_column(String(20), nullable=False, default="pendente")
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "status_upload IN ('pendente','concluido','falha')",
            name="ck_adaptacoes_status",
        ),
        Index("ix_adaptacoes_usuario_criado", "usuario_id", "criado_em"),
        Index("ix_adaptacoes_documento", "documento_id"),
        # RN-20: idempotência por (usuario, cache_key) apenas quando concluído
        Index(
            "ux_adaptacoes_usuario_cache",
            "usuario_id",
            "cache_key",
            unique=True,
            postgresql_where=("status_upload = 'concluido'"),
        ),
    )


class EventoXP(Base):
    __tablename__ = "eventos_xp"
    evento_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_uuid
    )
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.usuario_id", ondelete="CASCADE"), nullable=False
    )
    adaptacao_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("adaptacoes.adaptacao_id", ondelete="CASCADE"),
        nullable=False,
    )
    tipo: Mapped[str] = mapped_column(String(30), nullable=False)
    xp: Mapped[int] = mapped_column(Integer, nullable=False)
    item_indice: Mapped[int | None] = mapped_column(Integer, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint("tipo IN ('geracao_conteudo','acerto_quiz')", name="ck_eventos_tipo"),
        # XP uma vez por pergunta e adaptação
        Index(
            "ux_eventos_acerto_quiz",
            "adaptacao_id",
            "item_indice",
            unique=True,
            postgresql_where=("tipo = 'acerto_quiz'"),
        ),
    )


class ConceitoProgresso(Base):
    __tablename__ = "conceitos_progresso"
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.usuario_id", ondelete="CASCADE"), primary_key=True
    )
    conceito: Mapped[str] = mapped_column(String(200), primary_key=True)
    nivel_origem: Mapped[str] = mapped_column(String(30), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="em_aprendizado")
    acertos_quiz: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    __table_args__ = (
        CheckConstraint("estado IN ('em_aprendizado','dominado')", name="ck_conceitos_estado"),
    )


class TesteNivel(Base):
    __tablename__ = "testes_nivel"
    teste_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.usuario_id", ondelete="CASCADE"), nullable=False
    )
    nivel_avaliado: Mapped[str] = mapped_column(String(30), nullable=False)
    perguntas: Mapped[dict] = mapped_column(JSONB, nullable=False)
    respostas: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    percentual_dominio: Mapped[float | None] = mapped_column(Numeric(4, 3), nullable=True)
    aprovado: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    tentativa: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (Index("ix_testes_usuario_criado", "usuario_id", "criado_em"),)
