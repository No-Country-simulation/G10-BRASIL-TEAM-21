from app.main import create_app
from app.schemas.adaptacao import AdaptacaoResponse
from app.schemas.common import VERSAO_SCHEMA


def test_versao_unica_em_todo_lugar():
    assert VERSAO_SCHEMA == "1.0"
    assert create_app().openapi()["info"]["version"] == VERSAO_SCHEMA
    assert AdaptacaoResponse.model_fields["versao_schema"].default == VERSAO_SCHEMA
