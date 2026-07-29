# ==============================================================================
# Multi-stage production Dockerfile for GrowthSpare IT Solutions Platform
# Base OS: Debian Bookworm Slim, Runtime: Python 3.13 (or stable 3.14 container)
# ==============================================================================

# Stage 1: Build dependencies & wheels
FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system utilities needed to compile native Python modules (C-extensions)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    libwebp-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency definition
COPY requirements.txt .

# Compile and package Python dependency wheels
RUN pip install --no-cache-dir --upgrade pip \
    && pip wheel --no-cache-dir --wheel-dir /app/wheels -r requirements.txt


# Stage 2: Clean final runtime image
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

WORKDIR /app

# Install system runtime requirements (dynamic library dependencies only, keeping container small)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libjpeg62-turbo \
    libwebp7 \
    zlib1g \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy packaged wheel dependencies from the builder stage
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# Install pre-compiled dependencies
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt \
    && rm -rf /wheels requirements.txt

# Create a non-privileged system user for process security mapping
RUN groupadd -g 1000 django \
    && useradd -u 1000 -g django -m -s /bin/bash djangouser

# Create directory matrices for static, media, and dynamic runtime operations
RUN mkdir -p /app/staticfiles /app/mediafiles \
    && chown -R djangouser:django /app

# Copy the application source code to container work directory
COPY --chown=djangouser:django . /app

# Switch process execution ownership to non-privileged user context
USER djangouser

# Expose standard default web server port mapping
EXPOSE 8000

# Perform container health checks via curl endpoint ping
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ping || exit 1

# Launch production application container using WSGI engine binding
CMD ["gunicorn", "--config", "deployment/gunicorn/gunicorn.conf.py", "config.wsgi:application"]