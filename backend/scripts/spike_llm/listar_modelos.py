import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("LLM_API_KEY")
if not api_key:
    raise ValueError("LLM_API_KEY não encontrada no arquivo .env")

client = genai.Client(api_key=api_key)
modelos = client.models.list()

print("Modelos de Geração:")
for modelo in modelos:
    if "generateContent" in (modelo.supported_actions or []):
        print(f"- {modelo.name}")

print("\nModelos de Embedding:")
for modelo in modelos:
    if "embedContent" in (modelo.supported_actions or []):
        print(f"- {modelo.name}")
