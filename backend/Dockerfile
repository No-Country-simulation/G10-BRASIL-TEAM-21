FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /srv

COPY pyproject.toml ./
# A mudança está aqui: instalar o pacote com as dependências de dev (ruff, pytest, httpx)
RUN pip install ".[dev]"

COPY app ./app
COPY alembic.ini ./
COPY migrations ./migrations
COPY tests ./tests

RUN useradd --system --uid 10001 --no-create-home app \
    && mkdir -p /srv/.local-storage \
    && chown -R app:app /srv
USER app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
