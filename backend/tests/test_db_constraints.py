import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError

from app.infra.db.models import Adaptacao, EventoXP, PerfilEvolucao

pytestmark = pytest.mark.integration


def test_jsonb_guarda_e_devolve_o_documento_inteiro(db_session, adaptacao_factory):
    resultado = {
        "metadados": {"formato_gerado": "Quiz", "conceitos_chave": ["VCN", "Ação"]},
        "conteudo_adaptado": {"itens": [{"pergunta": "p"}]},
        "analogias": None,
    }
    a = adaptacao_factory(resultado=resultado)
    db_session.expire_all()
    assert db_session.get(Adaptacao, a.adaptacao_id).resultado == resultado


def test_jsonb_consulta_por_chave_interna(db_session, adaptacao_factory):
    a = adaptacao_factory(resultado={"metadados": {"formato_gerado": "Quiz"}})
    adaptacao_factory(resultado={"metadados": {"formato_gerado": "Tutorial"}})
    quiz = db_session.scalars(
        select(Adaptacao.adaptacao_id).where(
            Adaptacao.resultado["metadados"]["formato_gerado"].as_string() == "Quiz",
            Adaptacao.usuario_id == a.usuario_id,
        )
    ).all()
    assert quiz == [a.adaptacao_id]


def test_jsonb_contem(db_session, adaptacao_factory):
    a = adaptacao_factory(resultado={"metadados": {"formato_gerado": "Quiz"}, "x": 1})
    n = db_session.scalar(
        select(func.count())
        .select_from(Adaptacao)
        .where(
            Adaptacao.adaptacao_id == a.adaptacao_id,
            Adaptacao.resultado.contains({"metadados": {"formato_gerado": "Quiz"}}),
        )
    )
    assert n == 1


def _xp(a, item):
    return EventoXP(
        usuario_id=a.usuario_id,
        adaptacao_id=a.adaptacao_id,
        tipo="acerto_quiz",
        xp=5,
        item_indice=item,
    )


def test_xp_acerto_quiz_duplicado_e_barrado(db_session, adaptacao_factory):
    a = adaptacao_factory()
    db_session.add(_xp(a, 0))
    db_session.commit()
    db_session.add(_xp(a, 0))
    with pytest.raises(IntegrityError) as erro:
        db_session.commit()
    db_session.rollback()
    assert "ux_eventos_acerto_quiz" in str(erro.value)


def test_xp_de_outra_pergunta_e_permitido(db_session, adaptacao_factory):
    a = adaptacao_factory()
    db_session.add_all([_xp(a, 0), _xp(a, 1)])
    db_session.commit()


def test_indice_parcial_nao_afeta_xp_de_geracao(db_session, adaptacao_factory):
    a = adaptacao_factory()
    for _ in range(2):
        db_session.add(
            EventoXP(
                usuario_id=a.usuario_id, adaptacao_id=a.adaptacao_id, tipo="geracao_conteudo", xp=10
            )
        )
    db_session.commit()


def test_xp_total_negativo_e_barrado(db_session, usuario):
    db_session.add(
        PerfilEvolucao(usuario_id=usuario.usuario_id, nivel_atual="Iniciante", xp_total=-1)
    )
    with pytest.raises(IntegrityError) as erro:
        db_session.commit()
    db_session.rollback()
    assert "ck_perfil_xp_nonneg" in str(erro.value)


def test_xp_total_zero_e_valido(db_session, usuario):
    db_session.add(
        PerfilEvolucao(usuario_id=usuario.usuario_id, nivel_atual="Iniciante", xp_total=0)
    )
    db_session.commit()


def test_extensao_vector_funciona(db_session):
    # A coluna embedding so chega na 0002; aqui provamos que a extensao esta ativa e operante.
    assert db_session.scalar(text("SELECT '[1,2,3]'::vector <-> '[1,2,4]'::vector")) == 1.0
