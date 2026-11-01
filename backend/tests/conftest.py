import os
import uuid

import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

load_dotenv()

# A MÁGICA: Se não tem DATABASE_URL, usa SQLite local
if "DATABASE_URL" not in os.environ:
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["JWT_SECRET"] = "chave-super-secreta-de-teste-123456"
    os.environ["JWT_EXPIRA_MIN"] = "60"

from app.api._deps import get_current_user  # noqa: E402
from app.config import get_settings  # noqa: E402
from app.infra.db.models import Adaptacao, Base, Documento, Usuario  # noqa: E402
from app.main import app  # noqa: E402


def pytest_configure(config):
    config.addinivalue_line("markers", "integration: depende do PostgreSQL do Compose")
    config.addinivalue_line("markers", "migration: roda alembic em banco descartavel")


# A MÁGICA 2: Pula os testes de integração se estiver usando SQLite local
def pytest_collection_modifyitems(config, items):
    if "sqlite" in os.environ.get("DATABASE_URL", ""):
        skip_integration = pytest.mark.skip(reason="Requer PostgreSQL (Rode via Docker)")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)


@pytest.fixture(scope="session")
def engine():
    eng = create_engine(get_settings().database_url, pool_pre_ping=True)
    try:
        with eng.connect():
            pass
    except OperationalError:
        pytest.skip("Banco indisponivel")

    if "sqlite" in str(eng.url):
        Base.metadata.create_all(bind=eng)

    yield eng
    eng.dispose()


@pytest.fixture
def db_session(engine):
    conexao = engine.connect()
    transacao = conexao.begin()
    sessao = Session(bind=conexao, join_transaction_mode="create_savepoint")
    yield sessao
    sessao.close()
    transacao.rollback()
    conexao.close()


@pytest.fixture
def usuario(db_session):
    u = Usuario(
        nome="T",
        email=f"{uuid.uuid4().hex}@exemplo.com",
        senha_hash="x",
        nivel_declarado="Iniciante",
    )
    db_session.add(u)
    db_session.commit()
    return u


@pytest.fixture
def adaptacao_factory(db_session, usuario):
    def _criar(**sobrescrever) -> Adaptacao:
        doc = Documento(
            usuario_id=usuario.usuario_id,
            titulo="T",
            formato_origem="texto",
            hash_conteudo=uuid.uuid4().hex,
        )
        db_session.add(doc)
        db_session.commit()
        campos = dict(
            usuario_id=usuario.usuario_id,
            documento_id=doc.documento_id,
            perfil_destinatario="Iniciante",
            formato_saida="Quiz",
            nicho_setor="Geral",
            nivel_detalhe="Didatico",
            nivel_do_usuario_no_momento="Iniciante",
            cache_key=uuid.uuid4().hex,
            resultado={},
            ancoragem_fonte_score=0.9,
            status_upload="concluido",
        )
        campos.update(sobrescrever)
        a = Adaptacao(**campos)
        db_session.add(a)
        db_session.commit()
        return a

    return _criar


@pytest.fixture(autouse=True)
def mock_auth():
    fake_user = Usuario(
        usuario_id=uuid.UUID("123e4567-e89b-12d3-a456-426614174000"),
        nome="Teste",
        email="teste@teste.com",
        nivel_declarado="Iniciante",
    )
    app.dependency_overrides[get_current_user] = lambda: fake_user
    yield
    app.dependency_overrides.clear()
