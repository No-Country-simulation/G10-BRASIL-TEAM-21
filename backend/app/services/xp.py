"""Gamificação (T13.2): ganho e perda de XP, perfil de evolução e trilha.

Tabela de XP escolhida pelo grupo (ideia_contagem_de_xp.md):
  upload de documento (só a 1ª vez) +10 · geração de conteúdo +5 · acerto no quiz +15 ·
  erro no quiz -2 (o XP total nunca fica abaixo de 0).
Limiares acumulados para liberar o Teste de Nível: 100, 300, 700 e 1500 (modo demo: x0,1).

Nada aqui faz commit: quem chama grava resultado e XP na mesma transação (RNF-14).
"""

import uuid
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..config import get_settings
from ..infra.db.models import EventoXP, PerfilEvolucao, Usuario
from ..schemas.adaptacao import TrilhaEvolucao
from ..schemas.enums import Nivel

# ---- Valores de XP (mude aqui se o grupo recalibrar) ----
XP_UPLOAD = 10
XP_GERACAO = 5
XP_ACERTO_QUIZ = 15
PENALIDADE_ERRO_QUIZ = 2
# Gerações que pontuam por dia civil. None = sem limite (a tabela do grupo não prevê teto).
TETO_GERACOES_POR_DIA: int | None = None

LIMIAR_APROVACAO = 0.7
FUSO = ZoneInfo("America/Sao_Paulo")

TIPO_UPLOAD = "upload_documento"
TIPO_GERACAO = "geracao_conteudo"
TIPO_ACERTO = "acerto_quiz"
TIPO_ERRO = "erro_quiz"

# XP acumulado que libera o Teste de Nível de cada nível. O último nível não tem.
LIMIARES: dict[Nivel, int] = {
    Nivel.INICIANTE: 100,  # Iniciante -> Dev Júnior
    Nivel.BASICO: 300,  # Dev Júnior -> Dev Pleno
    Nivel.INTERMEDIARIO: 700,  # Dev Pleno -> Tech Lead
    Nivel.AVANCADO: 1500,  # Tech Lead -> Arquiteto
}
ORDEM_NIVEIS = list(Nivel)


# ---------- regras puras (sem banco) ----------


def nivel_de(texto: str | None) -> Nivel:
    try:
        return Nivel(texto) if texto else Nivel.INICIANTE
    except ValueError:
        return Nivel.INICIANTE


def limiar_do_nivel(nivel: Nivel, modo_demo: bool = False) -> int | None:
    """XP acumulado para liberar o Teste de Nível; None no nível máximo."""
    base = LIMIARES.get(nivel)
    if base is None:
        return None
    return max(1, round(base * 0.1)) if modo_demo else base


def teste_nivel_disponivel(nivel: Nivel, xp_total: int, modo_demo: bool = False) -> bool:
    limiar = limiar_do_nivel(nivel, modo_demo)
    return limiar is not None and xp_total >= limiar


def montar_trilha(
    perfil: PerfilEvolucao,
    *,
    xp_ganho_sessao: int = 0,
    xp_disponivel_ao_validar: int = 0,
    modo_demo: bool = False,
) -> TrilhaEvolucao:
    nivel = nivel_de(perfil.nivel_atual)
    limiar = limiar_do_nivel(nivel, modo_demo)
    proximo = ORDEM_NIVEIS[ORDEM_NIVEIS.index(nivel) + 1] if limiar is not None else None
    progresso = 100.0 if not limiar else round(min(perfil.xp_total / limiar, 1.0) * 100, 1)
    return TrilhaEvolucao(
        nivel_atual=nivel,
        proximo_nivel=proximo,
        xp_total=perfil.xp_total,
        xp_ganho_nesta_sessao=xp_ganho_sessao,
        xp_disponivel_ao_validar=xp_disponivel_ao_validar,
        xp_para_proximo_nivel=limiar or 0,
        progresso_percentual=progresso,
        conceitos_dominados=[],  # entram com o Teste de Nível (conceitos_progresso)
        conceitos_em_aprendizado=[],
        teste_nivel_disponivel=teste_nivel_disponivel(nivel, perfil.xp_total, modo_demo),
        limiar_aprovacao=LIMIAR_APROVACAO,
        sugestao_promocao=False,
    )


# ---------- com banco ----------


def obter_perfil(db: Session, usuario: Usuario) -> PerfilEvolucao:
    """Devolve o perfil do usuário, criando com 0 XP na primeira vez (nível = o declarado)."""
    perfil = db.get(PerfilEvolucao, usuario.usuario_id)
    if perfil is None:
        perfil = PerfilEvolucao(
            usuario_id=usuario.usuario_id,
            nivel_atual=nivel_de(usuario.nivel_declarado).value,
            xp_total=0,
        )
        db.add(perfil)
        db.flush()
    return perfil


def perfil_ou_padrao(db: Session, usuario: Usuario) -> PerfilEvolucao:
    """Perfil existente ou um padrão (0 XP) que NÃO é gravado. Para rotas que só leem."""
    perfil = db.get(PerfilEvolucao, usuario.usuario_id)
    if perfil is None:
        perfil = PerfilEvolucao(
            usuario_id=usuario.usuario_id,
            nivel_atual=nivel_de(usuario.nivel_declarado).value,
            xp_total=0,
        )
    return perfil


def _geracoes_hoje(db: Session, usuario_id: uuid.UUID) -> int:
    """Quantas gerações já pontuaram no dia civil de America/Sao_Paulo."""
    inicio = datetime.now(FUSO).replace(hour=0, minute=0, second=0, microsecond=0)
    return (
        db.scalar(
            select(func.count())
            .select_from(EventoXP)
            .where(
                EventoXP.usuario_id == usuario_id,
                EventoXP.tipo == TIPO_GERACAO,
                EventoXP.criado_em >= inicio,
                EventoXP.criado_em < inicio + timedelta(days=1),
            )
        )
        or 0
    )


def registrar_geracao(db: Session, usuario: Usuario, adaptacao_id: uuid.UUID) -> int:
    """+5 XP pela adaptação gerada. Devolve o XP concedido (0 no teto diário).

    A adaptação precisa já estar no banco (flush), pois o evento aponta para ela.
    """
    perfil = obter_perfil(db, usuario)
    if TETO_GERACOES_POR_DIA is not None and (
        _geracoes_hoje(db, usuario.usuario_id) >= TETO_GERACOES_POR_DIA
    ):
        return 0
    db.add(
        EventoXP(
            usuario_id=usuario.usuario_id,
            adaptacao_id=adaptacao_id,
            tipo=TIPO_GERACAO,
            xp=XP_GERACAO,
        )
    )
    perfil.xp_total += XP_GERACAO
    db.flush()
    return XP_GERACAO


def registrar_upload(db: Session, usuario: Usuario, documento_id: uuid.UUID) -> int:
    """+10 XP na primeira vez que o usuário sobe um documento. Reenvio (mesmo hash) dá 0.

    O reenvio devolve o mesmo documento_id (ver ingestao.py), e o índice único
    (usuario_id, documento_id) do banco impede o XP de ser pago duas vezes.
    """
    perfil = obter_perfil(db, usuario)
    try:
        with db.begin_nested():  # savepoint: conflito não desfaz o upload
            db.add(
                EventoXP(
                    usuario_id=usuario.usuario_id,
                    documento_id=documento_id,
                    tipo=TIPO_UPLOAD,
                    xp=XP_UPLOAD,
                )
            )
    except IntegrityError:
        return 0
    perfil.xp_total += XP_UPLOAD
    db.flush()
    return XP_UPLOAD


def _inserir_evento_unico(db: Session, evento: EventoXP) -> bool:
    """Grava o evento num savepoint. False se o índice único recusou (já existia)."""
    try:
        with db.begin_nested():
            db.add(evento)
    except IntegrityError:
        return False
    return True


def registrar_quiz(
    db: Session,
    usuario: Usuario,
    adaptacao_id: uuid.UUID,
    acertos: list[int],
    erros: list[int],
) -> int:
    """Aplica o XP de um envio de respostas. Devolve o saldo (pode ser negativo).

    - acerto: +15, uma vez por pergunta e adaptação;
    - erro: -2, uma vez por pergunta e adaptação, e só se a pergunta ainda não foi acertada
      (quem já pontuou a pergunta não é punido por errá-la depois);
    - errar e depois acertar: a penalidade antiga fica e o acerto ainda soma +15;
    - o XP total nunca fica abaixo de 0: ganhos entram primeiro, depois as penalidades,
      e cada penalidade é limitada ao XP que existe.
    Reenviar as mesmas respostas devolve saldo 0. O índice único do banco é a garantia final
    contra duas requisições simultâneas.
    """
    perfil = obter_perfil(db, usuario)
    existentes = db.execute(
        select(EventoXP.tipo, EventoXP.item_indice).where(
            EventoXP.adaptacao_id == adaptacao_id, EventoXP.tipo.in_([TIPO_ACERTO, TIPO_ERRO])
        )
    ).all()
    ja_acertou = {i for tipo, i in existentes if tipo == TIPO_ACERTO}
    ja_errou = {i for tipo, i in existentes if tipo == TIPO_ERRO}

    ganho = 0
    for indice in sorted(set(acertos) - ja_acertou):
        evento = EventoXP(
            usuario_id=usuario.usuario_id,
            adaptacao_id=adaptacao_id,
            tipo=TIPO_ACERTO,
            xp=XP_ACERTO_QUIZ,
            item_indice=indice,
        )
        if _inserir_evento_unico(db, evento):
            ganho += XP_ACERTO_QUIZ
    perfil.xp_total += ganho

    perda = 0
    for indice in sorted(set(erros) - ja_acertou - ja_errou):
        aplicada = min(PENALIDADE_ERRO_QUIZ, perfil.xp_total)  # piso em 0
        evento = EventoXP(
            usuario_id=usuario.usuario_id,
            adaptacao_id=adaptacao_id,
            tipo=TIPO_ERRO,
            xp=-aplicada,  # registra o que foi de fato descontado (pode ser 0)
            item_indice=indice,
        )
        if _inserir_evento_unico(db, evento):
            perfil.xp_total -= aplicada
            perda += aplicada

    db.flush()
    return ganho - perda


def modo_demo() -> bool:
    return bool(get_settings().adaptai_modo_demo)  # RN-16