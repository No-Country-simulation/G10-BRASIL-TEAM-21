"""Regras puras sobre a escada de níveis.

"Pura" significa: dado o mesmo argumento, devolve sempre o mesmo resultado,
sem ler banco, relógio ou rede. Por isso é fácil de testar sem mocks.
"""

from app.domain.enums import Nivel

# A ordem desta tupla É a escada de evolução. Tupla (e não lista) porque
# não deve ser alterada em tempo de execução.
ESCADA: tuple[Nivel, ...] = (
    Nivel.INICIANTE,
    Nivel.JUNIOR,
    Nivel.PLENO,
    Nivel.TECH_LEAD,
    Nivel.ARQUITETO,
)


def posicao(nivel: Nivel) -> int:
    """Devolve o degrau do nível: Iniciante = 0, ..., Arquiteto = 4."""
    return ESCADA.index(nivel)


def proximo_nivel(nivel: Nivel) -> Nivel | None:
    """Devolve o nível seguinte, ou None se já for o máximo (Arquiteto).

    Usado na promoção: o nível só sobe por aprovação no Teste de Nível.
    """
    i = posicao(nivel)
    # Se ainda existe um degrau acima, devolve; senão chegou ao topo.
    return ESCADA[i + 1] if i + 1 < len(ESCADA) else None


def tem_descompasso(
    nivel_documento: Nivel | None, nivel_usuario: Nivel, limite: int = 2
) -> bool:
    """RN-09: o documento está muito acima (ou abaixo) do nível do usuário?

    Há descompasso quando a diferença de degraus é >= `limite` (padrão 2).
    O sistema só ALERTA, nunca bloqueia (RN-08).

    Se o nível do documento não foi estimado (None, por exemplo porque o LLM
    estava fora do ar na ingestão), nunca há alerta.
    """
    if nivel_documento is None:
        return False
    # abs() porque o descompasso vale nos dois sentidos: documento muito
    # difícil OU muito fácil para o usuário.
    return abs(posicao(nivel_documento) - posicao(nivel_usuario)) >= limite
