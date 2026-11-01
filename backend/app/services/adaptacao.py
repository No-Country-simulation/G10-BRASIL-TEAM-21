"""Serviço de adaptação (T11): recupera chunks, chama o agente e monta a resposta do contrato."""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..agents.adaptacao import AgenteFalhouError, executar_cadeia
from ..agents.prompts import montar_sistema, montar_usuario
from ..api._errors import ErroApi
from ..infra.db.models import Chunk, Documento, Usuario
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
from ..schemas.enums import DominioConhecimento, Nivel, StatusUpload

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
        # Texto enviado direto: fatia em memória (sem embeddings, nada é gravado).
        blocos = dividir_em_chunks(payload.documento_conteudo or "")[:MAX_CHUNKS_CONTEXTO]
        trechos = [(f"chunk-{i + 1:03d}", b.texto) for i, b in enumerate(blocos)]
        return payload.documento_titulo or "Texto enviado", "texto-enviado", trechos, None

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


def gerar_adaptacao(
    db: Session,
    usuario: Usuario,
    payload: AdaptacaoRequest,
    cadeia: list[LLMProvider],
    request_id: str,
    incluir_gabarito: bool = False,
) -> AdaptacaoResponse:
    titulo_doc, documento_ref, trechos, doc = _selecionar_trechos(db, usuario, payload)
    if not trechos:
        raise ErroApi(400, "REQUISICAO_INVALIDA", "O documento não tem conteúdo para adaptar.")

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

    saida = resultado.saida
    # RN-11: só vale citar chunk que realmente foi enviado à IA.
    validos = {chunk_id for chunk_id, _ in trechos}
    com_fonte = 0
    for item in saida.itens:
        item.fontes_chunks = [c for c in item.fontes_chunks if c in validos]
        com_fonte += bool(item.fontes_chunks)
    ancoragem = round(com_fonte / len(saida.itens), 3)

    resposta = AdaptacaoResponse(
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
    return resposta if incluir_gabarito else ocultar_gabarito(resposta)