FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

COPY pyproject.toml /app/
RUN uv pip install --system -r pyproject.toml 2>/dev/null || pip install --no-cache-dir \
    "fastapi[standard]>=0.115.0" \
    "sqlmodel>=0.0.22" \
    "alembic>=1.13.0" \
    "psycopg[binary]>=3.1.0" \
    "pydantic>=2.7.0" \
    "pydantic-settings>=2.2.0" \
    "python-multipart>=0.0.9" \
    "pyjwt>=2.8.0" \
    "pwdlib[argon2,bcrypt]>=0.2.0" \
    "httpx>=0.27.0" \
    "jinja2>=3.1.3" \
    "email-validator>=2.1.0"

COPY alembic.ini /app/
COPY app /app/app/
COPY scripts /app/scripts/

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
