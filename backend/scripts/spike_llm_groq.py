import json
import os
import time

from dotenv import load_dotenv
from google import genai
from groq import Groq
from pydantic import BaseModel, ValidationError

# ==========================================
# 1. CONFIGURAÇÃO DE AMBIENTE
# ==========================================
load_dotenv()

LLM_API_KEY = os.getenv("LLM_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("ERRO: GROQ_API_KEY não encontrada no .env")

client_gemini = genai.Client(api_key=LLM_API_KEY) if LLM_API_KEY else None
client_groq = Groq(api_key=GROQ_API_KEY)

# ==========================================
# 2. CONTRATOS PYDANTIC
# ==========================================
class Flashcard(BaseModel):
    pergunta: str
    resposta: str

class Quiz(BaseModel):
    pergunta: str
    opcoes: list[str]
    resposta_correta: str

class Resumo(BaseModel):
    topicos_principais: list[str]
    resumo_geral: str

class AdaptacaoOutput(BaseModel):
    conteudo: list[Flashcard] | list[Quiz] | Resumo

# ==========================================
# 3. DEFINIÇÃO DOS 3 CENÁRIOS
# ==========================================
CENARIOS = [
    {
        "nome": "Cenário 1: Saúde / Iniciante / Flashcards",
        "texto": (
            "A hipertensão arterial é uma condição crônica em que a pressão arterial "
            "está persistentemente elevada."
        ),
        "perfil": "Iniciante",
        "formato": "Flashcards",
        "nicho": "Saude"
    },
    {
        "nome": "Cenário 2: Código / Dev Pleno / Quiz",
        "texto": "O FastAPI é um framework web moderno em Python baseado no padrão ASGI.",
        "perfil": "Desenvolvedor Pleno",
        "formato": "Quiz",
        "nicho": "Codigo"
    },
    {
        "nome": "Cenário 3: Fintech / Gestor / Resumo Executivo (Doc Longo)",
        "texto": (
            "Relatório de resultados do terceiro trimestre. A receita líquida cresceu "
            "15% em relação ao ano anterior. "
        ) * 5,
        "perfil": "Gestor",
        "formato": "Resumo Executivo",
        "nicho": "Fintech"
    }
]

# ==========================================
# 4. TESTE DE GERAÇÃO E MÉTRICAS (AGORA COM GROQ)
# ==========================================
def rodar_cenario(cenario):
    print(f"\n{'='*60}")
    print(f"▶ {cenario['nome']}")
    print(f"{'='*60}")

    # Extrai o schema JSON do Pydantic para mandar no prompt do Groq
    schema_json = json.dumps(AdaptacaoOutput.model_json_schema(), indent=2)

    prompt = f"""
    Você é um especialista em adaptação de conteúdo educacional.
    Adapte o texto abaixo para o perfil '{cenario['perfil']}' no formato '{cenario['formato']}'.
    Nicho: {cenario['nicho']}

    Você DEVE retornar APENAS um JSON válido seguindo estritamente este schema:
    {schema_json}

    TEXTO BASE:
    {cenario['texto']}
    """

    latencias = []
    json_validos = 0
    total_tokens = 0
    execucoes = 3

    for i in range(execucoes):
        inicio = time.perf_counter()
        try:
            # MODELO ATUALIZADO PARA O NOVO PADRÃO GRATUITO DA GROQ
            response = client_groq.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.4
            )
            fim = time.perf_counter()

            latencia = fim - inicio
            latencias.append(latencia)

            # Valida o JSON retornado
            texto_resposta = response.choices[0].message.content
            if texto_resposta is None:
                raise ValueError("Resposta do Groq sem conteúdo textual")

            AdaptacaoOutput.model_validate_json(texto_resposta)
            json_validos += 1

            # Tokens do Groq
            usage = response.usage
            if usage is not None and usage.total_tokens is not None:
                total_tokens += usage.total_tokens

            print(f"  Execução {i+1}: {latencia:.2f}s (JSON Válido)")

            time.sleep(2)

        except ValidationError:
            print(f"  Execução {i+1}: Erro de Validação Pydantic")
        except ValueError as e:
            print(f"  Execução {i+1}: Resposta inválida - {e}")
        except Exception as e:
            print(f"  Execução {i+1}: Erro na API - {e}")

    print("\n  📊 Resultados do Cenário:")
    print(f"  - Taxa de JSON Válido: {json_validos}/{execucoes}")
    if latencias:
        print(f"  - Latência Média: {sum(latencias)/len(latencias):.2f}s")
    print(f"  - Tokens Gastos: {total_tokens}")
    print("  - Custo: R$ 0,00 (Free Tier Groq)")

# ==========================================
# 5. JUIZ DE FIDELIDADE (Usando Groq)
# ==========================================
def testar_juiz_fidelidade():
    print(f"\n{'='*60}")
    print("▶ TESTE DO JUIZ DE FIDELIDADE (Alucinação)")
    print(f"{'='*60}")

    texto_original = "O FastAPI foi criado por Sebastián Ramírez em 2018."
    texto_com_mentira = "O FastAPI foi criado por Sebastián Ramírez em 2020."

    prompt = f"""
    Avalie se o TEXTO ADAPTADO é fiel ao TEXTO ORIGINAL.
    Se houver qualquer informação inventada ou alterada, responda APENAS 'INFIEL'.
    Se estiver fiel, responda APENAS 'FIEL'.

    TEXTO ORIGINAL: {texto_original}
    TEXTO ADAPTADO: {texto_com_mentira}
    """

    response = client_groq.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}]
    )
    resposta = response.choices[0].message.content
    if resposta is None:
        raise ValueError("Resposta do juiz Groq sem conteúdo textual")

    resultado = resposta.strip().upper()
    print(f"  Adaptado c/ Erro: {texto_com_mentira}")
    print(f"  Resposta do Juiz: {resultado}")

    if "INFIEL" in resultado:
        print("  ✅ SUCESSO: O juiz detectou a alucinação.")
    else:
        print("  ❌ FALHA: O juiz não detectou a mentira.")

# ==========================================
# 6. EMBEDDINGS (Ainda usando Gemini, pois tem cota de 1500 RPD)
# ==========================================
def testar_embeddings():
    print(f"\n{'='*60}")
    print("▶ TESTE DE EMBEDDINGS (Dimensão N)")
    print(f"{'='*60}")

    if not client_gemini:
        print("  ⚠️ Pulando embeddings: LLM_API_KEY do Gemini não configurada.")
        return

    try:
        response = client_gemini.models.embed_content(
            model='gemini-embedding-001',
            contents="Texto de teste para medir a dimensão do vetor."
        )
        if not response.embeddings:
            raise ValueError("Resposta do Gemini sem embeddings")

        valores_embedding = response.embeddings[0].values
        if valores_embedding is None:
            raise ValueError("Embedding retornado sem valores")

        dimensao_n = len(valores_embedding)
        print("  Modelo escolhido: gemini-embedding-001")
        print(f"  DIMENSÃO N: {dimensao_n}")
        print(f"  👉 AVISAR A FRENTE A: Coluna do banco deve ser Vector({dimensao_n})")
    except Exception as e:
        print(f"  Erro ao gerar embedding: {e}")

if __name__ == "__main__":
    print("🚀 INICIANDO SPIKE DA T3 - ADAPT AI (VIA GROQ)")

    for cenario in CENARIOS:
        rodar_cenario(cenario)

    testar_juiz_fidelidade()
    testar_embeddings()

    print("\n✅ Spike finalizado! Use os dados acima para preencher o ADR-0011.")
