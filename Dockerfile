# Dev-friendly image for FastAPI + Postgres client
FROM python:3.12-slim

WORKDIR /app

# System deps needed by psycopg2-binary (libpq)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 gcc && \
    rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir watchfiles  # enables --reload
    
RUN pip check

# App code
COPY . .

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

EXPOSE 8000

# Uvicorn dev server with autoreload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
