"""Cria o usuário demo caso ele não exista."""

from sqlalchemy import select

from app.core.security import hash_senha
from app.infra.db.models import Usuario

# Puxamos a função _fabrica (ou o nome que estiver no seu session.py)
from app.infra.db.session import _fabrica


def seed_demo_user():
    # Instancia a sessão igual ao seu get_db faz
    db = _fabrica()()
    try:
        email_demo = "demo@adaptai.com.br"

        # Verifica se o usuário demo já existe
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
            pass
    except Exception:
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_user()
