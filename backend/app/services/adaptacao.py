"""Serviço de adaptação: recupera fontes, usa cache e persiste o resultado gerado."""

import hashlib
import json
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..agents.adaptacao import AgenteFalhouError, executar_cadeia
from ..agents.prompts import montar_sistema, montar_usuario
from ..api._errors import ErroApi
from ..infra.db.models import Adaptacao, Chunk, Documento, Usuario
from ..ports.llm import LLMProvider
from ..rag.chunker import dividir_em_chunks
from ..rag.embeddings import ErroEmbedding
from ..rag.retrieval import buscar_chunks_similares
from ..schemas.adaptacao import (
    AdaptacaoRequest,
    AdaptacaoResponse,
    ArmazenamentoOCI,
    AvaliacaoQualidade,
    ConteudoAdaptado,
    Metadados,
    ocultar_gabarito,
)
from ..schemas.adaptacao_output import SAIDA_POR_FORMATO
from ..schemas.enums import DominioConhecimento, FormatoSaida, Nivel, StatusUpload

# IMPORT DA T13
from . import xp

# Doc 04: documentos de até ~12 chunks vão inteiros para o contexto; acima disso, busca top-k.
MAX_CHUNKS_CONTEXTO = 12
TOP_K = 6


def _enum_ou_none(tipo, valor):
    try:
        return tipo(valor) if valor else None
    except ValueError:
        return None


def _selecionar_trechos(
    db: Session, usuario: Usuario, payload: AdaptacaoRequest
) -> tuple[str, str, list[tuple[str, str]], Documento | None]:
    """Devolve (titulo, id_do_documento, [(chunk_id, texto)], documento) para o prompt."""
    if payload.documento_id is None:
        # Documento inline também precisa de um registro-pai, pois Adaptacao exige FK.
        conteudo = payload.documento_conteudo or ""
        bytes_conteudo = conteudo.encode("utf-8")
        hash_conteudo = hashlib.sha256(bytes_conteudo).hexdigest()
        doc = db.scalars(
            select(Documento).where(
                Documento.usuario_id == usuario.usuario_id,
                Documento.hash_conteudo == hash_conteudo,
            )
        ).first()
        if doc is None:
            doc = Documento(
                usuario_id=usuario.usuario_id,
                titulo=payload.documento_titulo or "Texto enviado",
                formato_origem="texto",
                hash_conteudo=hash_conteudo,
                tamanho_bytes=len(bytes_conteudo),
                status_upload="concluido",
            )
            db.add(doc)
            db.flush()

        blocos = dividir_em_chunks(conteudo)[:MAX_CHUNKS_CONTEXTO]
        trechos = [(f"chunk-{i + 1:03d}", b.texto) for i, b in enumerate(blocos)]
        return (
            payload.documento_titulo or doc.titulo,
            str(doc.documento_id),
            trechos,
            doc,
        )

    try:
        doc_uuid = uuid.UUID(payload.documento_id)
    except ValueError:
        raise ErroApi(400, "REQUISICAO_INVALIDA", "documento_id inválido.") from None
    doc = db.scalars(
        select(Documento).where(
            Documento.documento_id == doc_uuid, Documento.usuario_id == usuario.usuario_id
        )
    ).first()
    if doc is None:
        raise ErroApi(404, "RECURSO_NAO_ENCONTRADO", "Documento não encontrado.")

    todos = list(
        db.scalars(
            select(Chunk).where(Chunk.documento_id == doc.documento_id).order_by(Chunk.ordem)
        )
    )
    if len(todos) <= MAX_CHUNKS_CONTEXTO:
        escolhidos = todos
    else:
        try:
            achados = buscar_chunks_similares(
                db,
                f"{doc.titulo}. Conceitos principais para {payload.formato_saida.value}",
                usuario.usuario_id,
                limite=TOP_K,
                documento_id=doc.documento_id,
            )
        except ErroEmbedding as exc:
            raise ErroApi(
                502, "LLM_INDISPONIVEL", "Não foi possível buscar os trechos do documento."
            ) from exc

        escolhidos = sorted((a.chunk for a in achados), key=lambda c: c.ordem)
    return doc.titulo, str(doc.documento_id), [(c.chunk_id, c.texto) for c in escolhidos], doc


def _gerar_cache_key(
    usuario: Usuario,
    documento: Documento,
    titulo_prompt: str,
    payload: AdaptacaoRequest,
    incluir_gabarito: bool,
) -> str:
    """Hash canônico de todos os dados que podem alterar a adaptação."""
    dados = {
        "schema": "1.0",
        "documento_id": str(documento.documento_id),
        "documento_hash": documento.hash_conteudo,
        "documento_titulo": titulo_prompt,
        "perfil_destinatario": payload.perfil_destinatario.value,
        "formato_saida": payload.formato_saida.value,
        "nicho_setor": payload.nicho_setor.value,
        "nivel_detalhe": payload.nivel_detalhe.value,
        "incluir_analogias": payload.incluir_analogias,
        "incluir_microlearning": payload.incluir_microlearning,
        "incluir_gabarito": incluir_gabarito,
        "usuario_id": str(usuario.usuario_id),
    }
    canonico = json.dumps(dados, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonico.encode("utf-8")).hexdigest()


def _resposta_do_cache(
    adaptacao: Adaptacao, request_id: str, incluir_gabarito: bool
) -> AdaptacaoResponse:
    """Reconstitui o JSONB e aplica os dados atuais da adaptação."""
    dados = dict(adaptacao.resultado or {})

    dados["adaptacao_id"] = str(adaptacao.adaptacao_id)

    resposta = AdaptacaoResponse.model_validate(dados).model_copy(
        update={
            "request_id": request_id,
            "cache_hit": True,
        }
    )

    return resposta if incluir_gabarito else ocultar_gabarito(resposta)


def gerar_adaptacao(
    db: Session,
    usuario: Usuario,
    payload: AdaptacaoRequest,
    cadeia: list[LLMProvider],
    request_id: str,
    incluir_gabarito: bool = False,
    forcar_reprocessamento: bool = False,
) -> AdaptacaoResponse:
    titulo_doc, documento_ref, trechos, doc = _selecionar_trechos(db, usuario, payload)
    if not trechos:
        raise ErroApi(400, "REQUISICAO_INVALIDA", "O documento não tem conteúdo para adaptar.")
    if doc is None:
        raise ErroApi(500, "ERRO_INTERNO", "Não foi possível registrar o documento da adaptação.")

    cache_key = _gerar_cache_key(usuario, doc, titulo_doc, payload, incluir_gabarito)
    adaptacao_existente = db.scalars(
        select(Adaptacao).where(
            Adaptacao.usuario_id == usuario.usuario_id,
            Adaptacao.cache_key == cache_key,
            Adaptacao.status_upload == "concluido",
        )
    ).first()

    if adaptacao_existente is not None and not forcar_reprocessamento:
        resposta_cache = _resposta_do_cache(adaptacao_existente, request_id, incluir_gabarito)
        perfil = xp.perfil_ou_padrao(db, usuario)
        xp_disponivel = (
            len(resposta_cache.conteudo_adaptado.itens) * xp.XP_ACERTO_QUIZ
            if resposta_cache.metadados.formato_gerado == FormatoSaida.QUIZ
            else 0
        )
        resposta_cache.trilha_evolucao = xp.montar_trilha(
            perfil, xp_disponivel_ao_validar=xp_disponivel
        )
        return resposta_cache

    schema = SAIDA_POR_FORMATO[payload.formato_saida]
    sistema = montar_sistema(
        perfil=payload.perfil_destinatario,
        formato=payload.formato_saida,
        nicho=payload.nicho_setor.value,
        nivel_detalhe=payload.nivel_detalhe.value,
        schema=schema,
    )
    usuario_prompt = montar_usuario(titulo=titulo_doc, trechos=trechos)

    try:
        resultado = executar_cadeia(cadeia, sistema, usuario_prompt, schema)
    except AgenteFalhouError as exc:
        if exc.so_saida_invalida:
            raise ErroApi(
                422, "VALIDACAO_FALHOU", "A IA não gerou um conteúdo válido. Tente novamente."
            ) from exc
        raise ErroApi(
            502, "LLM_INDISPONIVEL", "Os provedores de IA estão indisponíveis. Tente mais tarde."
        ) from exc

    saida: Any = resultado.saida
    validos = {chunk_id for chunk_id, _ in trechos}
    com_fonte = 0
    for item in saida.itens:
        item.fontes_chunks = [c for c in item.fontes_chunks if c in validos]
        com_fonte += bool(item.fontes_chunks)
    ancoragem = round(com_fonte / len(saida.itens), 3)

    resposta = AdaptacaoResponse(
        adaptacao_id="pendente",
        request_id=request_id,
        metadados=Metadados(
            perfil_aplicado=payload.perfil_destinatario,
            formato_gerado=payload.formato_saida,
            nicho_aplicado=payload.nicho_setor,
            dominio_conhecimento=_enum_ou_none(
                DominioConhecimento, doc.dominio_conhecimento if doc else None
            ),
            nivel_detalhe=payload.nivel_detalhe,
            tempo_estimado_estudo_minutos=saida.tempo_estimado_estudo_minutos,
            conceitos_chave=saida.conceitos_chave,
            pre_requisitos=saida.pre_requisitos,
            nivel_documento_estimado=_enum_ou_none(
                Nivel, doc.nivel_documento_estimado if doc else None
            ),
            alerta_descompasso=False,
        ),
        conteudo_adaptado=ConteudoAdaptado(
            titulo=saida.titulo,
            introducao_contextualizada=saida.introducao_contextualizada,
            itens=saida.itens,
        ),
        avaliacao_qualidade=AvaliacaoQualidade(
            ancoragem_fonte_score=ancoragem,
            clareza_pedagogica="não avaliada",
            chunks_utilizados=len(trechos),
            observacoes=(
                f"Gerado por {resultado.provedor} ({resultado.modelo})"
                + (" após falha do provedor principal." if resultado.usou_fallback else ".")
            ),
        ),
        armazenamento_oci=ArmazenamentoOCI(
            bucket="",
            objeto_id="",
            documento_original_id=documento_ref,
            status_upload=StatusUpload.PENDENTE,
        ),
    )

    # --- LÓGICA DE PERSISTÊNCIA (T12) + XP (T13) ---

    # Variável para armazenar o XP que foi ganho nesta sessão
    xp_ganho = 0

    if adaptacao_existente is None:
        adaptacao_existente = Adaptacao(
            usuario_id=usuario.usuario_id,
            documento_id=doc.documento_id,
            perfil_destinatario=payload.perfil_destinatario.value,
            formato_saida=payload.formato_saida.value,
            nicho_setor=payload.nicho_setor.value,
            nivel_detalhe=payload.nivel_detalhe.value,
            nivel_do_usuario_no_momento=usuario.nivel_declarado,
            cache_key=cache_key,
            resultado=resposta.model_dump(mode="json"),
            ancoragem_fonte_score=ancoragem,
            status_upload="concluido",
        )
        db.add(adaptacao_existente)
        db.flush()  # Garante que a adaptacao_id exista antes de dar o XP
        resposta.adaptacao_id = str(adaptacao_existente.adaptacao_id)
        adaptacao_existente.resultado = resposta.model_dump(mode="json")

        # AQUI DÁ O XP DA T13! (+5 XP)
        xp_ganho = xp.registrar_geracao(db, usuario, adaptacao_existente.adaptacao_id)
    else:
        resposta.adaptacao_id = str(adaptacao_existente.adaptacao_id)
        adaptacao_existente.resultado = resposta.model_dump(mode="json")
        adaptacao_existente.ancoragem_fonte_score = ancoragem
        adaptacao_existente.status_upload = "concluido"

    # Atualiza a trilha na resposta
    perfil = xp.perfil_ou_padrao(db, usuario)
    xp_disponivel = (
        len(saida.itens) * xp.XP_ACERTO_QUIZ if payload.formato_saida == FormatoSaida.QUIZ else 0
    )
    resposta.trilha_evolucao = xp.montar_trilha(
        perfil,
        xp_ganho_sessao=xp_ganho,
        xp_disponivel_ao_validar=xp_disponivel,
    )
    # O JSON persistido precisa conter a trilha atual para respostas de cache.
    adaptacao_existente.resultado = resposta.model_dump(mode="json")

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        concorrente = db.scalars(
            select(Adaptacao).where(
                Adaptacao.usuario_id == usuario.usuario_id,
                Adaptacao.cache_key == cache_key,
                Adaptacao.status_upload == "concluido",
            )
        ).first()
        if concorrente is None or forcar_reprocessamento:
            raise
        return _resposta_do_cache(concorrente, request_id, incluir_gabarito)

    return resposta if incluir_gabarito else ocultar_gabarito(resposta)
