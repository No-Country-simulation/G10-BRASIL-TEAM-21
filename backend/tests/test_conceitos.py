"""Testes das regras de conceitos e do Teste de Nível."""

from app.domain.conceitos import (
    aprovado,
    conceitos_fracos,
    percentual_dominio,
    registrar_acerto_quiz,
    registrar_acerto_teste_nivel,
)
from app.domain.enums import EstadoConceito


def test_primeiro_acerto_de_quiz_nao_domina():
    estado, acertos = registrar_acerto_quiz(EstadoConceito.EM_APRENDIZADO, 0)
    assert estado == EstadoConceito.EM_APRENDIZADO
    assert acertos == 1


def test_segundo_acerto_de_quiz_domina():
    estado, acertos = registrar_acerto_quiz(EstadoConceito.EM_APRENDIZADO, 1)
    assert estado == EstadoConceito.DOMINADO
    assert acertos == 2


def test_conceito_dominado_nunca_retrocede():
    estado, _ = registrar_acerto_quiz(EstadoConceito.DOMINADO, 5)
    assert estado == EstadoConceito.DOMINADO


def test_acerto_no_teste_de_nivel_domina_na_hora():
    assert (
        registrar_acerto_teste_nivel(EstadoConceito.EM_APRENDIZADO)
        == EstadoConceito.DOMINADO
    )


def test_percentual_sem_respostas_e_zero():
    assert percentual_dominio([]) == 0.0


def test_percentual_todos_certos_e_um():
    respostas = [("VCN", True), ("Sub-redes", True)]
    assert percentual_dominio(respostas) == 1.0


def test_cada_conceito_pesa_igual():
    # VCN: 1 pergunta, acertou (100%). Sub-redes: 4 perguntas, acertou 1 (25%).
    # Média por conceito = (1.0 + 0.25) / 2 = 0.625.
    # Se pesasse por pergunta seria 2/5 = 0.4: o teste protege a diferença.
    respostas = [
        ("VCN", True),
        ("Sub-redes", True),
        ("Sub-redes", False),
        ("Sub-redes", False),
        ("Sub-redes", False),
    ]
    assert percentual_dominio(respostas) == 0.625


def test_aprovacao_no_limite_de_70_por_cento():
    # RN-07: 70% ou mais aprova.
    assert aprovado(0.7) is True
    assert aprovado(0.69) is False


def test_conceitos_fracos_listados_na_ordem():
    respostas = [
        ("VCN", True),
        ("Sub-redes", False),
        ("Security Lists", False),
        ("Security Lists", True),
    ]
    # VCN 100% (ok), Sub-redes 0% (fraco), Security Lists 50% (fraco).
    assert conceitos_fracos(respostas) == ["Sub-redes", "Security Lists"]


def test_sem_conceitos_fracos_quando_tudo_certo():
    assert conceitos_fracos([("VCN", True)]) == []
