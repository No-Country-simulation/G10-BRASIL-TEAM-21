"""Enumerações do domínio do AdaptAI.

Os valores (o texto à direita do "=") são os que aparecem no JSON da API.
Por convenção do projeto (doc 07), ficam em PT-BR SEM acentos. Não "corrija"
para "Júnior": o contrato da API exige "Junior".

Este arquivo é do domínio: não faz I/O (sem banco, rede ou disco).
"""

# StrEnum (Python 3.11+): cada membro É uma string. Assim "Nivel.INICIANTE"
# serializa direto para "Iniciante" no JSON e pode ser comparado com texto.
from enum import StrEnum


class Nivel(StrEnum):
    """Os 5 degraus da trilha de evolução (RN-01). Um por usuário."""

    INICIANTE = "Iniciante"
    JUNIOR = "Desenvolvedor Junior"
    PLENO = "Desenvolvedor Pleno"
    TECH_LEAD = "Tech Lead"
    ARQUITETO = "Arquiteto"


class PerfilSaida(StrEnum):
    """Para quem o conteúdo é escrito em cada requisição (RN-02).

    São os 5 níveis acima + Gestor/Executivo, que fica FORA da escada de
    níveis (o usuário nunca "evolui" para Gestor).
    """

    INICIANTE = "Iniciante"
    JUNIOR = "Desenvolvedor Junior"
    PLENO = "Desenvolvedor Pleno"
    TECH_LEAD = "Tech Lead"
    ARQUITETO = "Arquiteto"
    GESTOR_EXECUTIVO = "Gestor/Executivo"


class FormatoSaida(StrEnum):
    """Os 5 formatos de pacote educacional que o sistema gera (RF-07)."""

    TUTORIAL = "Tutorial"
    FLASHCARDS = "Flashcards"
    QUIZ = "Quiz"
    RESUMO_EXECUTIVO = "Resumo Executivo"
    ROTEIRO_AULA = "Roteiro de Aula"


class Nicho(StrEnum):
    """Setor de aplicação, que muda exemplos e vocabulário do conteúdo."""

    GERAL = "Geral"
    FINTECH = "Fintech"
    SAUDE = "Saude"
    E_COMMERCE = "E-commerce"


class NivelDetalhe(StrEnum):
    """Profundidade do conteúdo gerado."""

    DIDATICO = "Didatico"
    INTERMEDIARIO = "Intermediario"
    APROFUNDADO = "Aprofundado"


class StatusUpload(StrEnum):
    """Situação do envio ao OCI Object Storage (RN-17).

    O resultado é gravado primeiro no banco como PENDENTE; depois do envio
    ao bucket passa para CONCLUIDO ou FALHA. Falha no bucket não perde o
    resultado: um script reenvia as pendências.
    """

    PENDENTE = "pendente"
    CONCLUIDO = "concluido"
    FALHA = "falha"
