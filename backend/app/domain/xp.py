"""Regras puras de XP e de limiares de nível (RN-03, RN-04, RN-05, RN-16).

Nada aqui lê banco, relógio ou variável de ambiente. Os dados que dependem
do mundo externo (quantas gerações já pontuaram hoje, se o modo demo está
ligado) chegam por parâmetro. Assim os testes não precisam de mocks.
"""

from app.domain.enums import Nivel

# --- Valores de pontuação (doc 02, RN-03 e RN-04) ---
XP_POR_GERACAO = 10        # +10 XP por adaptação gerada
XP_POR_ACERTO_QUIZ = 5     # +5 XP por pergunta de quiz respondida corretamente
TETO_GERACOES_POR_DIA = 3  # só as 3 primeiras gerações do dia pontuam

# --- Limiares de XP ACUMULADO para liberar o Teste de Nível (RN-05) ---
# A chave é o nível ATUAL; o valor é o XP total necessário para tentar subir.
# Arquiteto não aparece: é o nível máximo, não há para onde subir.
# Estes números são ponto de partida para calibragem (PRD-003) e, no futuro,
# devem vir de um arquivo de configuração.
LIMIARES_XP: dict[Nivel, int] = {
    Nivel.INICIANTE: 100,
    Nivel.JUNIOR: 250,
    Nivel.PLENO: 450,
    Nivel.TECH_LEAD: 700,
}

# RN-16: no modo demo os limiares são multiplicados por 0,1 para mostrar a
# promoção de nível em minutos.
FATOR_MODO_DEMO = 0.1


def xp_por_geracao(geracoes_pontuadas_hoje: int) -> int:
    """XP ganho ao gerar uma adaptação (RN-03).

    `geracoes_pontuadas_hoje` é quantas gerações JÁ pontuaram no dia civil
    (America/Sao_Paulo), SEM contar a atual. A partir da 4ª geração do dia
    o usuário continua podendo gerar (RN-08: nunca bloqueia), mas não ganha XP.
    """
    if geracoes_pontuadas_hoje < TETO_GERACOES_POR_DIA:
        return XP_POR_GERACAO
    return 0


def xp_por_acerto_quiz(ja_pontuado: bool) -> int:
    """XP ganho ao acertar uma pergunta de quiz (RN-04).

    Cada pergunta de cada adaptação pontua UMA vez. `ja_pontuado` diz se esse
    acerto já foi contado antes. O banco também garante isso com um índice
    único; esta regra é a primeira linha de defesa.
    """
    return 0 if ja_pontuado else XP_POR_ACERTO_QUIZ


def limiar_para_subir(nivel: Nivel, modo_demo: bool = False) -> int | None:
    """XP total necessário para liberar o Teste de Nível a partir de `nivel`.

    Devolve None para o nível máximo (Arquiteto), que não tem limiar.
    """
    base = LIMIARES_XP.get(nivel)
    if base is None:
        return None
    if modo_demo:
        # max(1, ...) evita limiar zero caso a base ou o fator mudem um dia.
        return max(1, round(base * FATOR_MODO_DEMO))
    return base


def teste_nivel_disponivel(xp_total: int, nivel: Nivel, modo_demo: bool = False) -> bool:
    """O usuário já pode fazer o Teste de Nível? (RN-06)

    Sim quando o XP acumulado atinge o limiar do nível atual. O XP continua
    acumulando depois disso. No nível máximo nunca está disponível.
    """
    limiar = limiar_para_subir(nivel, modo_demo)
    if limiar is None:
        return False
    return xp_total >= limiar


def progresso_percentual(xp_total: int, nivel: Nivel, modo_demo: bool = False) -> int:
    """Progresso até o Teste de Nível, de 0 a 100 (campo `progresso_percentual`).

    É xp_total / limiar, limitado a 100. No nível máximo devolve 100.
    """
    limiar = limiar_para_subir(nivel, modo_demo)
    if limiar is None:
        return 100
    # min(..., 100): o XP continua acumulando além do limiar, mas a barra
    # de progresso não passa de 100%.
    return min(100, xp_total * 100 // limiar)
