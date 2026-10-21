import uuid
import pytest
from sqlalchemy.exc import IntegrityError
from app.infra.db.models import Usuario, Documento, Chunk, Adaptacao

pytestmark = pytest.mark.integration

def test_email_unico_por_lowercase(db_session):
    # Gera um e-mail único por execução
    email_unico = f"{uuid.uuid4().hex}@exemplo.com"

    u1 = Usuario(nome="A", email=email_unico, senha_hash="x", nivel_declarado="Iniciante")
    db_session.add(u1)
    db_session.commit()

    # Tenta inserir com maiúsculas, o índice lower() deve barrar
    u2 = Usuario(nome="B", email=email_unico.upper(), senha_hash="y", nivel_declarado="Iniciante")
    db_session.add(u2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

def test_tsvector_gerado_automaticamente(db_session):
    email_unico = f"{uuid.uuid4().hex}@exemplo.com"
    u = Usuario(nome="A", email=email_unico, senha_hash="x", nivel_declarado="Iniciante")
    db_session.add(u)
    db_session.commit()

    d = Documento(usuario_id=u.usuario_id, titulo="T", formato_origem="texto", hash_conteudo=uuid.uuid4().hex)
    db_session.add(d)
    db_session.commit()

    c = Chunk(documento_id=d.documento_id, chunk_id="c1", ordem=1, texto="A VCN é uma rede privada.")
    db_session.add(c)
    db_session.commit()

    # O PostgreSQL deve ter gerado o tsvector sozinho
    assert c.tsvector_conteudo is not None
    assert "vcn" in c.tsvector_conteudo

def test_cache_key_unico_quando_concluido(db_session):
    email_unico = f"{uuid.uuid4().hex}@exemplo.com"
    u = Usuario(nome="A", email=email_unico, senha_hash="x", nivel_declarado="Iniciante")
    db_session.add(u)
    db_session.commit()

    d = Documento(usuario_id=u.usuario_id, titulo="T", formato_origem="texto", hash_conteudo=uuid.uuid4().hex)
    db_session.add(d)
    db_session.commit()

    # Gera uma chave de cache única
    cache_key_unica = uuid.uuid4().hex

    a1 = Adaptacao(usuario_id=u.usuario_id, documento_id=d.documento_id, perfil_destinatario="Iniciante",
                   formato_saida="Quiz", nicho_setor="Geral", nivel_detalhe="Didatico",
                   nivel_do_usuario_no_momento="Iniciante", cache_key=cache_key_unica,
                   resultado={}, ancoragem_fonte_score=0.9, status_upload="concluido")
    db_session.add(a1)
    db_session.commit()

    # Tentar inserir o mesmo cache_key com status concluido deve falhar
    a2 = Adaptacao(usuario_id=u.usuario_id, documento_id=d.documento_id, perfil_destinatario="Iniciante",
                   formato_saida="Quiz", nicho_setor="Geral", nivel_detalhe="Didatico",
                   nivel_do_usuario_no_momento="Iniciante", cache_key=cache_key_unica,
                   resultado={}, ancoragem_fonte_score=0.9, status_upload="concluido")
    db_session.add(a2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
