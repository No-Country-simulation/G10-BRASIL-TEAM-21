import sys

from sqlalchemy import select

from app.core.security import hash_senha
from app.infra.db.models import Usuario
from app.infra.db.session import _fabrica


def seed_demo_user():
    db = None
    try:
        db = _fabrica()()
        email_demo = "demo@adaptai.com.br"
        user = db.scalars(select(Usuario).where(Usuario.email == email_demo)).first()

        if not user:
            demo_user = Usuario(
                nome="Usuário Demo",
                email=email_demo,
                senha_hash=hash_senha("demo123"),
                nivel_declarado="Iniciante",
            )
            db.add(demo_user)
            db.commit()
            print("✅ Usuário demo criado com sucesso!")
        else:
            print("ℹ️ Usuário demo já existe.")
    except Exception as e:
        print(f"⚠️ Aviso: Não foi possível criar o usuário demo. Motivo: {e}")
        if db:
            db.rollback()
        sys.exit(0)  # Força a saída com sucesso para não quebrar o Docker
    finally:
        if db:
            db.close()


if __name__ == "__main__":
    seed_demo_user()
