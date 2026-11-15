from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..infra.db.models import Usuario
from ..schemas.perfil import PerfilResponse
from ..services import xp
from ._deps import get_current_user, get_db

router = APIRouter(prefix="/perfil", tags=["perfil"])


@router.get("", response_model=PerfilResponse)
def obter_perfil(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PerfilResponse:
    perfil = xp.perfil_ou_padrao(db, current_user)
    trilha = xp.montar_trilha(perfil)
    return PerfilResponse(**trilha.model_dump())
