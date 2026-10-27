"""Gera docs/openapi.json (contrato publicado para o front)."""

import json
import os
from pathlib import Path

# A MÁGICA: Só define se a variável não existir no ambiente!
if "DATABASE_URL" not in os.environ:
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["JWT_SECRET"] = "chave-super-secreta-de-teste-123456"
    os.environ["JWT_EXPIRA_MIN"] = "60"

# ADICIONE O # noqa: E402 NO FINAL DESSA LINHA:
from app.main import create_app  # noqa: E402


def main() -> None:
    destino = Path(__file__).resolve().parents[2] / "docs" / "openapi.json"
    destino.parent.mkdir(parents=True, exist_ok=True)

    spec = create_app().openapi()
    destino.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"OpenAPI escrito em {destino}")


if __name__ == "__main__":
    main()
