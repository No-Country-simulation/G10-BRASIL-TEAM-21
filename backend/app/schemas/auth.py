"""Auth: cadastro, login, logout, usuário logado."""
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from .enums import Nivel


class CadastroRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nome: str = Field(min_length=1, max_length=200)
    email: EmailStr
    senha: str = Field(min_length=8, max_length=128)
    nivel_declarado: Nivel


class CadastroResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    usuario_id: str
    nome: str
    email: str
    nivel_atual: Nivel


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr
    senha: str = Field(min_length=1)


class LoginResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    access_token: str
    token_type: str = "bearer"
    expira_em_segundos: int


class UsuarioMeResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    usuario_id: str
    nome: str
    email: str
    nivel_atual: Nivel
