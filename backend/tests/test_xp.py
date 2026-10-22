"""Testes das regras de XP (RN-03, RN-04, RN-05, RN-16)."""

from app.domain.enums import Nivel
from app.domain.xp import (
    limiar_para_subir,
    progresso_percentual,
    teste_nivel_disponivel,
    xp_por_acerto_quiz,
    xp_por_geracao,
)


def test_primeira_geracao_do_dia_da_10_xp():
    assert xp_por_geracao(0) == 10


def test_terceira_geracao_do_dia_ainda_pontua():
    # Já pontuaram 2 hoje; a atual é a 3ª e ainda entra no teto.
    assert xp_por_geracao(2) == 10


def test_quarta_geracao_do_dia_nao_pontua():
    # Já pontuaram 3 hoje: teto atingido (RN-03).
    assert xp_por_geracao(3) == 0


def test_acerto_de_quiz_da_5_xp_uma_vez():
    assert xp_por_acerto_quiz(ja_pontuado=False) == 5


def test_acerto_repetido_nao_pontua_de_novo():
    # RN-04: cada pergunta pontua uma única vez por adaptação.
    assert xp_por_acerto_quiz(ja_pontuado=True) == 0


def test_limiares_do_doc_02():
    # RN-05: 100, 250, 450 e 700 de XP acumulado.
    assert limiar_para_subir(Nivel.INICIANTE) == 100
    assert limiar_para_subir(Nivel.JUNIOR) == 250
    assert limiar_para_subir(Nivel.PLENO) == 450
    assert limiar_para_subir(Nivel.TECH_LEAD) == 700


def test_arquiteto_nao_tem_limiar():
    # Nível máximo: não há para onde subir.
    assert limiar_para_subir(Nivel.ARQUITETO) is None


def test_modo_demo_divide_limiares_por_dez():
    # RN-16: fator 0,1 para demonstrar a promoção em minutos.
    assert limiar_para_subir(Nivel.INICIANTE, modo_demo=True) == 10
    assert limiar_para_subir(Nivel.JUNIOR, modo_demo=True) == 25
    assert limiar_para_subir(Nivel.PLENO, modo_demo=True) == 45
    assert limiar_para_subir(Nivel.TECH_LEAD, modo_demo=True) == 70


def test_teste_de_nivel_libera_ao_atingir_o_limiar():
    assert teste_nivel_disponivel(99, Nivel.INICIANTE) is False
    assert teste_nivel_disponivel(100, Nivel.INICIANTE) is True


def test_teste_de_nivel_continua_disponivel_com_xp_acima():
    # RN-06: o XP segue acumulando depois do limiar.
    assert teste_nivel_disponivel(180, Nivel.INICIANTE) is True


def test_arquiteto_nunca_tem_teste_de_nivel():
    assert teste_nivel_disponivel(5000, Nivel.ARQUITETO) is False


def test_progresso_percentual_igual_ao_exemplo_do_contrato():
    # Doc 05: 60 de 100 XP = 60%.
    assert progresso_percentual(60, Nivel.INICIANTE) == 60


def test_progresso_nao_passa_de_100():
    assert progresso_percentual(250, Nivel.INICIANTE) == 100


def test_progresso_do_arquiteto_e_100():
    assert progresso_percentual(0, Nivel.ARQUITETO) == 100
