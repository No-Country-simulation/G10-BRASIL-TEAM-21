import pytest
from pydantic import ValidationError

from app.config import Settings


def test_sem_jwt_secret_a_aplicacao_nao_sobe(monkeypatch):
    monkeypatch.delenv("JWT_SECRET", raising=False)

    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_variavel_vazia_conta_como_ausente(monkeypatch):
    monkeypatch.setenv("EMBEDDING_DIM", "")

    configuracao = Settings(_env_file=None)

    assert configuracao.embedding_dim is None
