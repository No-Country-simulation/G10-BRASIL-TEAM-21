"""Provedor falso: sem rede, devolve um JSON fixo e válido (CI e LLM_PROVIDER=fake)."""

import json

from pydantic import BaseModel

from ...schemas.adaptacao_output import AdaptacaoOutput


class FakeProvider:
    nome = "fake"
    modelo = "fake"

    def gerar_json(self, sistema: str, usuario: str, schema: type[BaseModel]) -> str:
        # Só sabemos fabricar flashcards; para outros formatos a validação falha de propósito.
        item = {
            "frente": "O que é um flashcard?",
            "verso": "Um cartão com pergunta de um lado e resposta do outro.",
            "dica_didatica": "Pense em revisar pouco, muitas vezes.",
            "conceito_ref": "flashcard",
            "fontes_chunks": ["chunk-001"],
        }
        corpo = {
            "titulo": "Flashcards de exemplo",
            "introducao_contextualizada": "Conteúdo de teste gerado sem chamar nenhum LLM.",
            "tempo_estimado_estudo_minutos": 5,
            "conceitos_chave": ["flashcard"],
            "pre_requisitos": [],
            "itens": [item],
        }
        assert issubclass(schema, AdaptacaoOutput)
        return json.dumps(corpo, ensure_ascii=False)