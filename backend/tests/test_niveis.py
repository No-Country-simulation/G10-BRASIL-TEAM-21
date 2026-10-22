"""Testes das regras de nível. Ficam soltos em tests/, como os demais."""

from app.domain.enums import Nivel
from app.domain.niveis import proximo_nivel, tem_descompasso


def test_proximo_nivel_do_iniciante_e_junior():
    # Caminho feliz: o degrau seguinte da escada.
    assert proximo_nivel(Nivel.INICIANTE) == Nivel.JUNIOR


def test_arquiteto_nao_tem_proximo_nivel():
    # Borda: o nível máximo não tem próximo, devolve None.
    assert proximo_nivel(Nivel.ARQUITETO) is None


def test_descompasso_com_dois_degraus():
    # Iniciante (0) x Pleno (2): diferença de 2, atinge o limite.
    assert tem_descompasso(Nivel.PLENO, Nivel.INICIANTE) is True


def test_sem_descompasso_com_um_degrau():
    # Iniciante (0) x Junior (1): diferença de 1, abaixo do limite.
    assert tem_descompasso(Nivel.JUNIOR, Nivel.INICIANTE) is False


def test_documento_sem_nivel_nunca_alerta():
    # RN-09: sem nível estimado do documento, nunca há alerta.
    assert tem_descompasso(None, Nivel.INICIANTE) is False


def test_descompasso_vale_nos_dois_sentidos():
    # Usuário Arquiteto lendo documento de Iniciante: também é descompasso.
    assert tem_descompasso(Nivel.INICIANTE, Nivel.ARQUITETO) is True


def test_valores_dos_enums_sem_acento():
    # Protege o contrato da API: ninguém pode trocar para "Júnior".
    assert Nivel.JUNIOR.value == "Desenvolvedor Junior"
