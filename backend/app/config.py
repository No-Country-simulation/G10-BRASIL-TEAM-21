"""Configuração lida do ambiente (docs/04 - Arquitetura.md, seção 11).

Nenhum segredo tem valor padrão: sem JWT_SECRET e DATABASE_URL a aplicação não sobe.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # env_ignore_empty: o Compose repassa variáveis vazias (ex.: OCI_REGION=);
    # elas contam como ausentes.
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_ignore_empty=True)

    adaptai_env: str = "dev"  # dev | demo | prod
    adaptai_modo_demo: bool = False  # RN-16

    jwt_secret: str
    jwt_expira_min: int = 60
    cors_origins: str = ""  # origens separadas por vírgula
    max_upload_mb: int = 10

    database_url: str

    storage_backend: str = "local"  # local | oci
    local_storage_dir: str = ".local-storage"
    oci_region: str | None = None
    oci_tenancy: str | None = None
    oci_user: str | None = None
    oci_fingerprint: str | None = None
    oci_key_file: str | None = None
    oci_namespace: str | None = None
    oci_bucket: str = "adaptai-conteudos-educativos"

    llm_provider: str | None = None
    llm_model: str | None = None
    llm_api_key: str | None = None

    # NOVAS VARIÁVEIS PARA A T11:
    llm_timeout_s: int = 60
    groq_api_key: str | None = None
    llm_fallback_provider: str | None = "groq"
    llm_fallback_model: str | None = "llama-3.1-8b-instant"

    embedding_model: str | None = None
    embedding_dim: int | None = None

    @property
    def cors_origin_list(self) -> list[str]:
        return [origem.strip() for origem in self.cors_origins.split(",") if origem.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore
