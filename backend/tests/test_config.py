from unittest.mock import patch

import pytest
from pydantic import ValidationError

from app.config import Settings


def test_sem_jwt_secret_a_aplicacao_nao_sobe():
    # Limpa as variáveis de ambiente para garantir que o JWT_SECRET não venha do sistema
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(ValidationError):
            # Passa database_url, mas omite JWT_SECRET.
            # O '_env_file=None' impede que o Pydantic leia o seu arquivo .env local.
            # O '# type: ignore' esconde o aviso do VS Code.
            Settings(database_url="postgresql://test", _env_file=None)  # type: ignore


def test_variavel_vazia_conta_como_ausente(monkeypatch):
    monkeypatch.setenv("EMBEDDING_DIM", "")

    # Passamos as obrigatórias para conseguir instanciar
    configuracao = Settings(
        jwt_secret="test_secret",
        database_url="postgresql://test",
        _env_file=None,  # type: ignore
    )

    assert configuracao.embedding_dim is None
