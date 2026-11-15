import os

from dotenv import find_dotenv, load_dotenv
from google import genai
from google.genai import types
from groq import Groq
from pydantic import BaseModel

# A MÁGICA AQUI: find_dotenv procura o .env em qualquer pasta acima
load_dotenv(find_dotenv(), override=True)


class RespostaTeste(BaseModel):
    mensagem: str
    sucesso: bool


def testar_gemini():
    print("\n--- TESTANDO GEMINI ---")
    api_key = os.getenv("LLM_API_KEY")
    modelo = os.getenv("LLM_MODEL", "gemini-3.8-flash")

    if not api_key:
        print("❌ LLM_API_KEY não encontrada no .env")
        return

    print(f"🔑 Chave encontrada: {api_key[:5]}...{api_key[-5:] if len(api_key) > 5 else ''}")
    print(f"🤖 Modelo: {modelo}")

    try:
        client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=15000),  # 15 segundos de timeout
        )
        response = client.models.generate_content(
            model=modelo,
            contents="Retorne um JSON de teste.",
            config=types.GenerateContentConfig(
                response_mime_type="application/json", response_schema=RespostaTeste
            ),
        )
        print(f"✅ SUCESSO GEMINI ({modelo})!")
        print(f"Resposta: {response.text}")
    except Exception as e:
        print(f"❌ ERRO NO GEMINI: {str(e)}")


def testar_groq():
    print("\n--- TESTANDO GROQ ---")
    api_key = os.getenv("GROQ_API_KEY")
    modelo = os.getenv("LLM_FALLBACK_MODEL", "openai/gpt-oss-20b")

    if not api_key:
        print("❌ GROQ_API_KEY não encontrada no .env")
        return

    print(f"🔑 Chave encontrada: {api_key[:5]}...{api_key[-5:] if len(api_key) > 5 else ''}")
    print(f"🤖 Modelo: {modelo}")

    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=modelo,
            messages=[
                {"role": "user", "content": "Retorne um JSON com as chaves 'mensagem' e 'sucesso'."}
            ],
            response_format={"type": "json_object"},
            timeout=15,
        )
        print(f"✅ SUCESSO GROQ ({modelo})!")
        print(f"Resposta: {response.choices[0].message.content}")
    except Exception as e:
        print(f"❌ ERRO NO GROQ: {str(e)}")


if __name__ == "__main__":
    testar_gemini()
    testar_groq()
