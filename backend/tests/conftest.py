import os

import pytest
from dotenv import load_dotenv

# 1. Carrega as variáveis do .env ANTES de importar o app
load_dotenv()

# Força as variáveis para o ambiente de teste local
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["JWT_SECRET"] = "chave-super-secreta-de-teste"
os.environ["JWT_EXPIRA_MIN"] = "60"

# 2. Imports do app (com o passe livre do Ruff # noqa: E402 em TODOS)
from app.api._deps import get_current_user  # noqa: E402
from app.infra.db.models import Usuario  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def mock_auth():
    fake_user = Usuario(
        usuario_id="123e4567-e89b-12d3-a456-426614174000",
        nome="Teste",
        email="teste@teste.com",
        nivel_declarado="Iniciante"
    )
    app.dependency_overrides[get_current_user] = lambda: fake_user
    yield
    app.dependency_overrides.clear()
