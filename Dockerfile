# Stage 1: Base build stage
FROM python:3.13-slim AS builder

RUN mkdir /my_app
WORKDIR /my_app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production stage
FROM python:3.13-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 && \
    useradd -m -r appuser && \
    mkdir /my_app && \
    chown -R root:root /my_app && \
    chmod -R 755 /my_app && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

WORKDIR /my_app

# Copy app code as root, but make specific folders writable if needed
COPY . .

# Optional: Make only specific folders writable by appuser
RUN mkdir -p /my_app/tmp && \
    chown -R appuser:appuser /my_app/tmp

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

USER appuser
EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "carehub.wsgi:application"]
