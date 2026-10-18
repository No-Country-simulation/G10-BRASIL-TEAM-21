"""Ambiente mínimo para os testes: sem rede, sem banco. Os segredos abaixo só valem nos testes."""

import os

os.environ.setdefault("JWT_SECRET", "segredo-somente-de-teste")
os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://teste:teste@localhost:5432/teste")
