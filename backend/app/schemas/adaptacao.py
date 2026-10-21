"""Requisição, resposta e avaliação de adaptação (v3)."""
from datetime import datetime
from typing import Union
from pydantic import BaseModel, ConfigDict, Field, model_validator

from .enums import (
    DominioConhecimento,
    FormatoSaida,
    Nivel,
    NivelDetalhe,
    Nicho,
    PerfilSaida,
    StatusUpload,
)
from .itens import (
    ItemConteudo,
    ItemFlashcard,
    ItemQuiz,
    ItemResumo,
    ItemRoteiroAula,
    ItemTutorial,
)


# ---------- Requisição ----------

class AdaptacaoRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    documento_id: str | None = None
    documento_titulo: str | None = None
    documento_conteudo: str | None = None
    perfil_destinatario: PerfilSaida
    formato_saida: FormatoSaida
    nicho_setor: Nicho
    nivel_detalhe: NivelDetalhe
    incluir_analogias: bool = False
    incluir_microlearning: bool = False

    @model_validator(mode="after")
    def _check_documento(self) -> "AdaptacaoRequest":
        titulo = self.documento_titulo
        conteudo = self.documento_conteudo
        parcial = (titulo is None) != (conteudo is None)
        if parcial:
            raise ValueError(
                "documento_titulo e documento_conteudo devem ser informados juntos."
            )
        tem_id = self.documento_id is not None
        tem_conteudo = titulo is not None and conteudo is not None
        if tem_id and tem_conteudo:
            raise ValueError(
                "Informe documento_id OU documento_titulo + documento_conteudo, nunca os dois."
            )
        if not tem_id and not tem_conteudo:
            raise ValueError(
                "Informe documento_id OU documento_titulo + documento_conteudo."
            )
        return self


# ---------- Blocos da resposta ----------

class Metadados(BaseModel):
    model_config = ConfigDict(extra="forbid")
    perfil_aplicado: PerfilSaida
    formato_gerado: FormatoSaida
    nicho_aplicado: Nicho
    dominio_conhecimento: DominioConhecimento | None = None  # v3
    nivel_detalhe: NivelDetalhe
    tempo_estimado_estudo_minutos: int
    conceitos_chave: list[str]
    pre_requisitos: list[str]
    nivel_documento_estimado: Nivel | None = None
    alerta_descompasso: bool


class ConteudoAdaptado(BaseModel):
    model_config = ConfigDict(extra="forbid")
    titulo: str
    introducao_contextualizada: str
    itens: list[ItemConteudo]


class MapeamentoAnalogia(BaseModel):
    model_config = ConfigDict(extra="forbid")
    termo_tecnico: str
    elemento_analogia: str


class Analogia(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    conceito: str
    estrategia: str
    analogia: str
    mapeamento: list[MapeamentoAnalogia]
    limite_da_analogia: str
    ancorada_na_fonte: bool = False
    conceito_ancorado_em: list[str]
    fontes_externas: list[str] = Field(default_factory=list)


class BlocoMicrolearning(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ordem: int
    titulo: str
    duracao_min: int
    itens_ref: list[int]
    objetivo: str


class Microlearning(BaseModel):
    model_config = ConfigDict(extra="forbid")
    duracao_total_min: int
    blocos: list[BlocoMicrolearning]


class AvaliacaoQualidade(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ancoragem_fonte_score: float
    fidelidade_analogias_score: float | None = None
    clareza_pedagogica: str  
    chunks_utilizados: int
    busca_hibrida: bool = False
    observacoes: str = ""


class TrilhaEvolucao(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nivel_atual: Nivel
    proximo_nivel: Nivel | None = None
    xp_total: int
    xp_ganho_nesta_sessao: int
    xp_disponivel_ao_validar: int
    xp_para_proximo_nivel: int
    progresso_percentual: float
    conceitos_dominados: list[str]
    conceitos_em_aprendizado: list[str]
    teste_nivel_disponivel: bool
    limiar_aprovacao: float
    sugestao_promocao: bool


class ArmazenamentoOCI(BaseModel):
    model_config = ConfigDict(extra="forbid")
    bucket: str
    objeto_id: str
    documento_original_id: str
    status_upload: StatusUpload


# ---------- Resposta completa ----------

class AdaptacaoResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: str = "sucesso"
    versao_schema: str = "1.0"
    request_id: str
    cache_hit: bool = False
    metadados: Metadados
    conteudo_adaptado: ConteudoAdaptado
    analogias: list[Analogia] | None = None
    microlearning: Microlearning | None = None
    avaliacao_qualidade: AvaliacaoQualidade
    trilha_evolucao: TrilhaEvolucao | None = None
    armazenamento_oci: ArmazenamentoOCI | None = None

    @model_validator(mode="after")
    def _consistencia_formato(self) -> "AdaptacaoResponse":
        formato = self.metadados.formato_gerado
        esperado = {
            FormatoSaida.FLASHCARDS: ItemFlashcard,
            FormatoSaida.QUIZ: ItemQuiz,
            FormatoSaida.TUTORIAL: ItemTutorial,
            FormatoSaida.RESUMO: ItemResumo,
            FormatoSaida.ROTEIRO_DE_AULA: ItemRoteiroAula,
        }.get(formato)
        if esperado is None:
            return self
        for i, item in enumerate(self.conteudo_adaptado.itens):
            if not isinstance(item, esperado):
                raise ValueError(
                    f"Item {i} nao e do tipo esperado para formato "
                    f"{formato.value}: esperado {esperado.__name__}, "
                    f"recebido {type(item).__name__}."
                )
        return self
