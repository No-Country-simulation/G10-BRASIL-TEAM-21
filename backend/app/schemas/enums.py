from enum import Enum
from typing import Final


class Nivel(str, Enum):
    """Posição canônica na escada de evolução (0–4). Universal, sem domínio.

    O rótulo exibido ao usuário depende do domínio (ver ROTULOS_NIVEL_POR_DOMINIO).
    Armazenamento, XP, limiares e Teste de Nível usam SEMPRE este enum.
    """
    INICIANTE = "Iniciante"
    BASICO = "Basico"
    INTERMEDIARIO = "Intermediario"
    AVANCADO = "Avancado"
    ESPECIALISTA = "Especialista"


class PerfilSaida(str, Enum):
    """Perfil de saída da adaptação. Os 5 níveis + o perfil fora da escada."""
    INICIANTE = "Iniciante"
    BASICO = "Basico"
    INTERMEDIARIO = "Intermediario"
    AVANCADO = "Avancado"
    ESPECIALISTA = "Especialista"
    GESTOR_EXECUTIVO = "Gestor/Executivo"


class FormatoSaida(str, Enum):
    TUTORIAL = "Tutorial"
    FLASHCARDS = "Flashcards"
    QUIZ = "Quiz"
    RESUMO = "Resumo"
    ROTEIRO_DE_AULA = "Roteiro de Aula"


class Nicho(str, Enum):
    GERAL = "Geral"
    FINTECH = "Fintech"
    SAUDE = "Saude"
    ECOMMERCE = "E-commerce"
    EDUCACAO = "Educacao"
    JURIDICO = "Juridico"


class NivelDetalhe(str, Enum):
    DIDATICO = "Didatico"
    INTERMEDIARIO = "Intermediario"
    APROFUNDADO = "Aprofundado"


class StatusUpload(str, Enum):
    PENDENTE = "pendente"
    CONCLUIDO = "concluido"
    FALHA = "falha"


class DominioConhecimento(str, Enum):
    """v3 — classificado na ingestão (RN-21)."""
    GERAL = "Geral"
    TI = "TI"
    MEDICINA = "Medicina"
    FINANCAS = "Financas"
    JURIDICO = "Juridico"
    ENGENHARIA = "Engenharia"
    EDUCACAO = "Educacao"


class ClassificadorUsado(str, Enum):
    LOCAL = "local"
    API = "api"
    FALLBACK = "fallback"


# --------------------------------------------------------------------------
# Rótulos de exibição por domínio. NÃO são valores de API; são texto de UI.
# O front consulta esse mapa (via GET /perfil ou /documentos) para exibir.
# --------------------------------------------------------------------------

ROTULOS_NIVEL_POR_DOMINIO: Final[dict[DominioConhecimento, dict[Nivel, str]]] = {
    DominioConhecimento.TI: {
        Nivel.INICIANTE: "Iniciante",
        Nivel.BASICO: "Desenvolvedor Junior",
        Nivel.INTERMEDIARIO: "Desenvolvedor Pleno",
        Nivel.AVANCADO: "Tech Lead",
        Nivel.ESPECIALISTA: "Arquiteto",
    },
    DominioConhecimento.MEDICINA: {
        Nivel.INICIANTE: "Iniciante",
        Nivel.BASICO: "Estudante",
        Nivel.INTERMEDIARIO: "Residente",
        Nivel.AVANCADO: "Especialista",
        Nivel.ESPECIALISTA: "Preceptor",
    },
    DominioConhecimento.FINANCAS: {
        Nivel.INICIANTE: "Iniciante",
        Nivel.BASICO: "Analista Junior",
        Nivel.INTERMEDIARIO: "Analista Pleno",
        Nivel.AVANCADO: "Gestor",
        Nivel.ESPECIALISTA: "CFO",
    },
    DominioConhecimento.JURIDICO: {
        Nivel.INICIANTE: "Iniciante",
        Nivel.BASICO: "Estagiario",
        Nivel.INTERMEDIARIO: "Advogado",
        Nivel.AVANCADO: "Socio",
        Nivel.ESPECIALISTA: "Jurista",
    },
    DominioConhecimento.ENGENHARIA: {
        Nivel.INICIANTE: "Iniciante",
        Nivel.BASICO: "Estagiario",
        Nivel.INTERMEDIARIO: "Engenheiro",
        Nivel.AVANCADO: "Engenheiro Senior",
        Nivel.ESPECIALISTA: "Perito",
    },
    DominioConhecimento.EDUCACAO: {
        Nivel.INICIANTE: "Iniciante",
        Nivel.BASICO: "Monitor",
        Nivel.INTERMEDIARIO: "Professor",
        Nivel.AVANCADO: "Coordenador",
        Nivel.ESPECIALISTA: "Diretor",
    },
    DominioConhecimento.GERAL: {
        Nivel.INICIANTE: "Iniciante",
        Nivel.BASICO: "Aprendiz",
        Nivel.INTERMEDIARIO: "Praticante",
        Nivel.AVANCADO: "Avancado",
        Nivel.ESPECIALISTA: "Especialista",
    },
}


def rotular_nivel(nivel: Nivel, dominio: DominioConhecimento) -> str:
    """Retorna o rótulo de exibição do nível para um domínio.

    Cai para o mapa GERAL se o domínio não tiver t  radução definida.
    """
    mapa = ROTULOS_NIVEL_POR_DOMINIO.get(
        dominio, ROTULOS_NIVEL_POR_DOMINIO[DominioConhecimento.GERAL]
    )
    return mapa[nivel]


def rotulos_disponiveis(dominio: DominioConhecimento) -> dict[str, str]:
    """Devolve {valor_canonico: rotulo_exibicao} para o front montar o select.

    Usado no endpoint GET /perfil (ou GET /meta/niveis?dominio=TI).
    """
    mapa = ROTULOS_NIVEL_POR_DOMINIO.get(
        dominio, ROTULOS_NIVEL_POR_DOMINIO[DominioConhecimento.GERAL]
    )
    return {nivel.value: rotulo for nivel, rotulo in mapa.items()}
