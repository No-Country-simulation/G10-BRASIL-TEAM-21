import uuid

import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.infra.db.models import Adaptacao, Documento, Usuario


def pytest_configure(config):
    config.addinivalue_line("markers", "integration: depende do PostgreSQL do Compose")
    config.addinivalue_line("markers", "migration: roda alembic em banco descartavel")


@pytest.fixture(scope="session")
def engine():
    eng = create_engine(get_settings().database_url, pool_pre_ping=True)
    try:
        with eng.connect():
            pass
    except OperationalError:
        pytest.skip("PostgreSQL indisponivel (docker compose up -d db)")
    if not inspect(eng).has_table("usuarios"):
        pytest.skip("Banco sem tabelas (docker compose exec backend alembic upgrade head)")
    yield eng
    eng.dispose()


@pytest.fixture
def db_session(engine):
    """Cada teste roda numa transacao externa descartada no fim: nada vai para o banco de dev."""
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