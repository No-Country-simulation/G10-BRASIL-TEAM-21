"""Gera docs/openapi.json (contrato publicado para o front).

Uso, a partir de backend/:  python -m scripts.export_openapi
"""

import json
from pathlib import Path

from app.main import create_app


def main() -> None:
    destino = Path(__file__).resolve().parents[2] / "docs" / "openapi.json"
    destino.parent.mkdir(parents=True, exist_ok=True)
    spec = create_app().openapi()
    destino.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"OpenAPI escrito em {destino}")


if __name__ == "__main__":
    main()
