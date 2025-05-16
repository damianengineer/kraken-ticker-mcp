# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS uv

# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Copy project files
COPY pyproject.toml .
COPY README.md .
COPY src/ ./src/

# Create a virtual environment and install the project's dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv venv && \
    uv pip install -e .

FROM python:3.12-slim-bookworm

WORKDIR /app
 
COPY --from=uv --chown=app:app /app/.venv /app/.venv
COPY --from=uv --chown=app:app /app/src /app/src

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Run the MCP server
ENTRYPOINT ["mcp-server-kraken"]
