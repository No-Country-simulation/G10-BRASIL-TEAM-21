from pydantic import BaseModel


class HealthResponse(BaseModel):
    api: str
    db: str
    pgvector: str
