"""T1.8 — enums alinhados ao contrato."""
from app.schemas.enums import (
    ClassificadorUsado,
    DominioConhecimento,
    FormatoSaida,
    Nivel,
    NivelDetalhe,
    Nicho,
    PerfilSaida,
    StatusUpload,
)


def test_formato_saida_tem_cinco_valores_e_resumo_sem_executivo():
    valores = {v.value for v in FormatoSaida}
    assert valores == {"Tutorial", "Flashcards", "Quiz", "Resumo", "Roteiro de Aula"}
    assert "Resumo Executivo" not in valores


def test_nicho_expandido_na_v3():
    valores = {v.value for v in Nicho}
    assert "Educacao" in valores
    assert "Juridico" in valores


def test_perfil_inclui_gestor_executivo():
    assert PerfilSaida.GESTOR_EXECUTIVO.value == "Gestor/Executivo"


def test_nivel_tem_cinco_degras():
    assert len(list(Nivel)) == 5


def test_dominio_e_classificador_existem():
    assert "TI" in {v.value for v in DominioConhecimento}
    assert {v.value for v in ClassificadorUsado} == {"local", "api", "fallback"}


def test_status_upload_sem_acento():
    assert {v.value for v in StatusUpload} == {"pendente", "concluido", "falha"}


def test_nivel_detalhe():
    assert {v.value for v in NivelDetalhe} == {"Didatico", "Intermediario", "Aprofundado"}
