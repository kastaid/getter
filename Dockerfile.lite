# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

FROM mwader/static-ffmpeg:7.1.1 AS builder_ffmpeg
FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:0.10.7 /uv /uvx /bin/
ENV TERM=xterm \
    PATH=/opt/venv/bin:$PATH \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv venv /opt/venv && \
    uv pip install -r requirements.txt
COPY --from=builder_ffmpeg /ffmpeg /usr/local/bin/ffmpeg
COPY --from=builder_ffmpeg /ffprobe /usr/local/bin/ffprobe
COPY . .
CMD ["python", "-m", "getter"]
