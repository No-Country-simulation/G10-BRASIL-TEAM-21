FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /srv

# Dependências primeiro
COPY pyproject.toml ./
RUN pip install .

COPY app ./app

# ADICIONE ESTAS DUAS LINHAS AQUI:
COPY alembic.ini ./
COPY migrations ./migrations

# Usuário sem privilégios
RUN useradd --system --uid 10001 --no-create-home app \
    && mkdir -p /srv/.local-storage \
    && chown -R app:app /srv
USER app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
