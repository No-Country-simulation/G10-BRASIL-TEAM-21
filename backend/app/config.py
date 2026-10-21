from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    adaptai_env: str = "dev"
    adaptai_modo_demo: bool = False
    jwt_secret: str
    jwt_expira_min: int = 60
    cors_origins: str = "http://localhost:5173"
    max_upload_mb: int = 10
    database_url: str
    storage_backend: str = "local"
    local_storage_dir: str = ".local-storage"

    oci_region: str = ""
    oci_tenancy: str = ""
    oci_user: str = ""
    oci_fingerprint: str = ""
    oci_key_file: str = ""
    oci_namespace: str = ""
    oci_bucket: str = "adaptai-conteudos-educativos"

    llm_provider: str = ""
    llm_model: str = ""
    llm_api_key: str = ""
    embedding_model: str = ""
    embedding_dim: int | None = None  # <-- Alterado para aceitar None

    @field_validator("embedding_dim", mode="before")
    @classmethod
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()  # type: ignore[call-arg]
    return _settings
