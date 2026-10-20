FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /srv

# Dependências primeiro: a camada fica em cache enquanto o pyproject.toml não mudar.
COPY pyproject.toml ./
RUN pip install .

COPY app ./app
# Quando existirem (US-008): COPY alembic.ini ./ e COPY migrations ./migrations

# Usuário sem privilégios; a pasta de armazenamento local precisa ser gravável por ele.
RUN useradd --system --uid 10001 --no-create-home app \
    && mkdir -p /srv/.local-storage \
    && chown -R app:app /srv
USER app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
