"""T1.8 — regra de documento_id XOR título+conteúdo."""
import pytest
from pydantic import ValidationError

from app.schemas.adaptacao import AdaptacaoRequest
from app.schemas.enums import FormatoSaida, NivelDetalhe, Nicho, PerfilSaida


def _base_kwargs() -> dict:
    return dict(
        perfil_destinatario=PerfilSaida.INICIANTE,
        formato_saida=FormatoSaida.FLASHCARDS,
        nicho_setor=Nicho.GERAL,
        nivel_detalhe=NivelDetalhe.DIDATICO,
    )


def test_aceita_documento_id_sozinho():
    AdaptacaoRequest(documento_id="doc-1", **_base_kwargs())


def test_aceita_titulo_e_conteudo_juntos():
    AdaptacaoRequest(
        documento_titulo="T",
        documento_conteudo="C",
        **_base_kwargs(),
    )


def test_rejeita_id_e_conteudo_juntos():
    with pytest.raises(ValidationError):
        AdaptacaoRequest(
            documento_id="doc-1",
            documento_titulo="T",
            documento_conteudo="C",
            **_base_kwargs(),
        )


def test_rejeita_sem_documento_nenhum():
    with pytest.raises(ValidationError):
        AdaptacaoRequest(**_base_kwargs())


def test_rejeita_titulo_sem_conteudo():
    with pytest.raises(ValidationError):
        AdaptacaoRequest(documento_titulo="T", **_base_kwargs())


def test_rejeita_conteudo_sem_titulo():
    with pytest.raises(ValidationError):
        AdaptacaoRequest(documento_conteudo="C", **_base_kwargs())
