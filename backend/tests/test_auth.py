import os
import uuid
from typing import cast

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Table, create_engine
from sqlalchemy.orm import sessionmaker

# FORÇA as variáveis de ambiente antes do app ser importado
os.environ["DATABASE_URL"] = "sqlite:///./test_auth.db"
os.environ["JWT_SECRET"] = "chave-super-secreta-de-teste"
os.environ["JWT_EXPIRA_MIN"] = "60"

from app.api._deps import get_current_user
from app.core.security import criar_token_jwt, decodificar_token, hash_senha, verificar_senha
from app.infra.db.models import Base, Usuario
from app.infra.db.session import get_db
from app.main import app

# ==========================================
# 1. SETUP DO BANCO EM ARQUIVO (SQLite)
# ==========================================
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_auth.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine, tables=[cast(Table, Usuario.__table__)])


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


# Apaga o arquivo do banco após rodar todos os testes
@pytest.fixture(scope="session", autouse=True)
def cleanup_db_file():
    yield
    # O dispose() fecha todas as conexões com o banco antes de apagarmos o arquivo
    engine.dispose()
    if os.path.exists("./test_auth.db"):
        try:
            os.remove("./test_auth.db")
        except PermissionError:
            pass  # Se o Windows travar, a gente ignora (o CI do Linux não trava)


# ==========================================
# 2. TESTES DAS FUNÇÕES DE SEGURANÇA (Unitários)
# ==========================================
def test_hash_e_verificacao_de_senha():
    senha = "minhaSenhaSuperSegura"
    senha_hash = hash_senha(senha)

    assert senha != senha_hash
    assert verificar_senha(senha, senha_hash) is True
    assert verificar_senha("senhaErrada", senha_hash) is False


def test_geracao_e_decodificacao_de_token():
    usuario_id = uuid.UUID("123e4567-e89b-12d3-a456-426614174000")
    token = criar_token_jwt(usuario_id)

    assert token is not None
    id_decodificado = decodificar_token(token)
    assert id_decodificado == usuario_id

    assert decodificar_token("token.falso.aqui") is None


# ==========================================
# 3. TESTES DAS ROTAS DE API
# ==========================================
@pytest.fixture(autouse=True)
def limpar_banco():
    """Limpa a tabela de usuários antes de cada teste."""
    db = TestingSessionLocal()
    db.query(Usuario).delete()
    db.commit()
    db.close()
    yield


def test_fluxo_completo_de_auth():
    # Instancia o client DENTRO do teste para evitar vazamento de threads
    with TestClient(app) as client:
        # 1. Cadastro
        payload_cadastro = {
            "nome": "Usuario Teste",
            "email": "teste@adaptai.com",
            "senha": "senha12345",
            "nivel_declarado": "Iniciante",
        }
        response = client.post("/api/v1/auth/cadastro", json=payload_cadastro)
        assert response.status_code == 201
        assert response.json()["email"] == "teste@adaptai.com"
        assert "usuario_id" in response.json()

        # 2. Tentar cadastrar o mesmo e-mail (deve dar erro 400)
        response_duplicado = client.post("/api/v1/auth/cadastro", json=payload_cadastro)
        assert response_duplicado.status_code == 400
        assert response_duplicado.json()["codigo"] == "EMAIL_EXISTE"

        # 3. Login com senha errada (deve dar erro 401)
        payload_login_errado = {"email": "teste@adaptai.com", "senha": "senha_errada"}
        response_erro = client.post("/api/v1/auth/login", json=payload_login_errado)
        assert response_erro.status_code == 401

        # 4. Login com sucesso
        payload_login = {"email": "teste@adaptai.com", "senha": "senha12345"}
        response_login = client.post("/api/v1/auth/login", json=payload_login)
        assert response_login.status_code == 200
        token = response_login.json()["access_token"]

        # 5. Acessar rota protegida (/me) com o token
        app.dependency_overrides.pop(get_current_user, None)

        headers = {"Authorization": f"Bearer {token}"}
        response_me = client.get("/api/v1/usuarios/me", headers=headers)

        assert response_me.status_code == 200
        assert response_me.json()["email"] == "teste@adaptai.com"
