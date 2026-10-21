"""Erros padronizados das rotas em stub."""
class NaoImplementadoError(Exception):
    """Sinaliza rota documentada mas ainda não implementada (HTTP 501)."""
