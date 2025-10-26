FROM python:3.11-slim

ARG USER_HOME=/app
WORKDIR ${USER_HOME}

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/base.txt requirements/base.txt
COPY requirements/dev.txt requirements/dev.txt
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install -r requirements/base.txt -r requirements/dev.txt

ENV PATH="/opt/venv/bin:${PATH}"

COPY . .

CMD ["python", "-m", "red_teaming.cli", "--help"]
