# syntax=docker/dockerfile:1.6

FROM python:3.11-slim as base

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_NO_SYNC_PROGRESS=1 \
    UV_PYTHON_BIN=python3.11 \
    UV_LINK_MODE=copy \
    PATH="/root/.local/bin:/root/.cargo/bin:${PATH}" \
    OLLAMA_HOST=0.0.0.0:11434 \
    OLLAMA_MODELS=/var/lib/ollama \
    WORKSHOP_HOME=/workspace

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        git \
        build-essential \
        tini \
        libssl-dev \
        libstdc++6 \
    && rm -rf /var/lib/apt/lists/*

# Install uv (Rust-based package manager)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Ollama CLI and server
RUN curl -fsSL https://ollama.com/install.sh | sh

# Pre-pull the qwen model during build so learners don't have to download it.
# The Ollama daemon must be running to pull models, so we launch it in the background,
# fetch the model, and then stop the daemon.
RUN mkdir -p "${OLLAMA_MODELS}" \
    && (OLLAMA_HOST=0.0.0.0:11434 ollama serve > /tmp/ollama.log 2>&1 &) \
    && sleep 5 \
    && OLLAMA_HOST=127.0.0.1:11434 ollama pull qwen:30b \
    && pkill -f "ollama serve" \
    && rm -f /tmp/ollama.log

WORKDIR ${WORKSHOP_HOME}

COPY pyproject.toml uv.lock* ./
COPY README.md .
COPY main.py .

COPY stages ./stages

# Create a non-root user for day-to-day workshop commands.
RUN useradd -ms /bin/bash workshop \
    && chown -R workshop:workshop ${WORKSHOP_HOME} \
    && chown -R workshop:workshop ${OLLAMA_MODELS}

USER workshop
WORKDIR ${WORKSHOP_HOME}

# Ensure uv will create environments within the workspace.
ENV UV_PROJECT_ENVIRONMENT="${WORKSHOP_HOME}/.venv"

# Pre-sync dependencies so containers are ready out of the box.
RUN uv sync --frozen --no-editable

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["bash"]
