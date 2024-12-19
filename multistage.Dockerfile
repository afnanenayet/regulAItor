FROM ghcr.io/astral-sh/uv:debian-slim

# ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
# First build the app into the /app directory
WORKDIR /app

# installing libgomp, required for streamlit
RUN apt-get update && apt-get install -y --no-install-recommends apt-utils
RUN apt-get -y install curl
RUN apt-get install libgomp1

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev --python 3.11.6
ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-dev --python 3.11.6

# Final image without uv
# FROM python:3.11-slim-bookworm
# It is important to use the image that matches the builder, as the path to the
# Python executable must be the same, e.g., using `python:3.11-slim-bookworm`
# will fail.

# Copy the application from the builder
# COPY --from=builder --chown=app:app /app /app

# Place executables in the environment at the front of the path
# ENV PATH="/app/.venv/bin:$PATH"
