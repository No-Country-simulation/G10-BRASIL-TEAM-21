"""Gera docs/openapi.json a partir do app FastAPI.

Uso: python -m backend.scripts.export_openapi  (a partir da raiz do backend/)
"""
import json
from pathlib import Path

from app.main import app


def main() -> None:
    spec = app.openapi()
    raiz = Path(__file__).resolve().parents[2]
    destino = raiz / "docs" / "openapi.json"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(
        json.dumps(spec, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"OpenAPI escrito em {destino}")


if __name__ == "__main__":
    main()
