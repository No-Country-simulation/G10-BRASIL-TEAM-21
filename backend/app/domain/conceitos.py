"""Regras puras de domínio de conceitos e de aprovação no Teste de Nível.

Cobre: quando um conceito vira "dominado" (doc 03, seção 4), o cálculo do
percentual de domínio e a aprovação (RN-07). Sem I/O: tudo chega por
parâmetro e volta como valor.
"""

from app.domain.enums import EstadoConceito

# Doc 03: um conceito passa a "dominado" ao acertar no Teste de Nível OU ao
# acumular 2 acertos em quizzes sobre ele.
ACERTOS_QUIZ_PARA_DOMINAR = 2

# RN-07: aprovação no Teste de Nível com domínio >= 70%.
LIMIAR_APROVACAO = 0.7


def registrar_acerto_quiz(
    estado: EstadoConceito, acertos_quiz: int
) -> tuple[EstadoConceito, int]:
    """Aplica um acerto de quiz a um conceito.

    Devolve (novo_estado, novo_total_de_acertos). Dois acertos acumulados
    tornam o conceito dominado. Se já era dominado, continua dominado:
    o estado nunca retrocede.
    """
    novos_acertos = acertos_quiz + 1
    if estado == EstadoConceito.DOMINADO or novos_acertos >= ACERTOS_QUIZ_PARA_DOMINAR:
        return EstadoConceito.DOMINADO, novos_acertos
    return EstadoConceito.EM_APRENDIZADO, novos_acertos


def registrar_acerto_teste_nivel(estado: EstadoConceito) -> EstadoConceito:
    """Acertar o conceito no Teste de Nível o torna dominado de imediato.

    O parâmetro `estado` fica na assinatura para a regra continuar valendo
    se um dia surgir um estado novo; hoje o resultado é sempre DOMINADO.
    """
    return EstadoConceito.DOMINADO


def percentual_dominio(respostas: list[tuple[str, bool]]) -> float:
    """Percentual de domínio de um Teste de Nível, de 0.0 a 1.0.

    `respostas` é uma lista de (conceito, acertou). Cada CONCEITO pesa igual,
    não importa quantas perguntas ele teve: calcula-se a fração de acertos de
    cada conceito e tira-se a média. Assim um conceito com 5 perguntas não
    "engole" um conceito com 1.

    ATENÇÃO: o doc 03 diz apenas "acertos ponderados por conceito", sem
    fórmula. Esta é a leitura mais simples; confirme com a equipe e, se
    mudar, ajuste aqui e nos testes.
    """
    if not respostas:
        return 0.0
    fracoes = _fracao_por_conceito(respostas)
    # round(..., 4) evita sujeira de ponto flutuante na comparação com 0.7.
    return round(sum(fracoes.values()) / len(fracoes), 4)


def aprovado(percentual: float, limiar: float = LIMIAR_APROVACAO) -> bool:
    """RN-07: aprovado quando o percentual de domínio é >= limiar."""
    return percentual >= limiar


def conceitos_fracos(
    respostas: list[tuple[str, bool]], limiar: float = LIMIAR_APROVACAO
) -> list[str]:
    """Conceitos com fração de acertos abaixo do limiar, na ordem em que
    apareceram. É o que o sistema mostra ao reprovado (RN-07).

    Escolha desta implementação: usar o mesmo limiar da aprovação como
    corte de "fraco". O doc não define; confirme com a equipe.
    """
    fracoes = _fracao_por_conceito(respostas)
    return [conceito for conceito, fracao in fracoes.items() if fracao < limiar]


def _fracao_por_conceito(respostas: list[tuple[str, bool]]) -> dict[str, float]:
    """Agrupa as respostas por conceito e devolve acertos / total de cada um.

    Função interna (prefixo "_"). Usa dict, que preserva a ordem de inserção
    no Python 3.7+, para manter a ordem de aparição dos conceitos.
    """
    total: dict[str, int] = {}
    acertos: dict[str, int] = {}
    for conceito, acertou in respostas:
        total[conceito] = total.get(conceito, 0) + 1
        acertos[conceito] = acertos.get(conceito, 0) + (1 if acertou else 0)
    return {c: acertos[c] / total[c] for c in total}
