# SPDX-License-Identifier: MPL-2.0

# Multi-stage Dockerfile for optimized production deployments
# Stage 1: Builder - Compile dependencies
FROM python:3.11-slim as builder

ARG VIRTUAL_ENV=/opt/venv
ENV VIRTUAL_ENV=${VIRTUAL_ENV} \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PATH="${VIRTUAL_ENV}/bin:$PATH"

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment and install dependencies
RUN python -m venv ${VIRTUAL_ENV} && \
    ${VIRTUAL_ENV}/bin/pip install --upgrade pip setuptools wheel

COPY requirements/base.txt requirements/base.txt
RUN ${VIRTUAL_ENV}/bin/pip install --no-cache-dir -r requirements/base.txt

# Stage 2: Runtime - Minimal image with only required runtime components
FROM python:3.11-slim

ARG VIRTUAL_ENV=/opt/venv
ARG APP_HOME=/app
ENV VIRTUAL_ENV=${VIRTUAL_ENV} \
    APP_HOME=${APP_HOME} \
    PATH="${VIRTUAL_ENV}/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install minimal runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 -d ${APP_HOME} appuser

# Copy virtual environment from builder
COPY --from=builder --chown=appuser:appuser ${VIRTUAL_ENV} ${VIRTUAL_ENV}

# Set working directory
WORKDIR ${APP_HOME}

# Copy only necessary application files (exclude tests, dev configs, etc.)
COPY --chown=appuser:appuser src/ src/
COPY --chown=appuser:appuser configs/ configs/
COPY --chown=appuser:appuser README.md LICENSE NOTICE .

# Create output directories
RUN mkdir -p reports logs && chown -R appuser:appuser reports logs

# Switch to non-root user
USER appuser

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; from red_teaming import setup_logging; setup_logging(); print('healthy')" || exit 1

# Default entrypoint
ENTRYPOINT ["python", "-m", "red_teaming.cli"]
CMD ["--help"]

# Labels for image metadata
LABEL org.opencontainers.image.title="Red Teaming Platform" \
      org.opencontainers.image.description="Vulnerability analysis and red-teaming for LLMs" \
      org.opencontainers.image.vendor="Red Team Platform" \
      org.opencontainers.image.licenses="MPL-2.0"
