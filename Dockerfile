# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

FROM mwader/static-ffmpeg:7.1.1 AS builder_ffmpeg

FROM python:3.12-slim-bookworm
ENV TERM=xterm \
    VIRTUAL_ENV=/opt/venv \
    PATH=/opt/venv/bin:/root/.local/bin:$PATH
ARG UV_VERSION=0.10.7
WORKDIR /app
COPY requirements.txt .
RUN set -eux && \
    apt-get -qqy update && \
    apt-get -qqy install --no-install-recommends \
        curl git ca-certificates && \
    curl -LsSf https://github.com/astral-sh/uv/releases/download/${UV_VERSION}/uv-installer.sh | sh && \
    python -m venv $VIRTUAL_ENV && \
    uv pip install --python $VIRTUAL_ENV/bin/python -r requirements.txt && \
    apt-get -qqy purge \
        curl && \
    apt-get -qqy autoremove && \
    apt-get clean

COPY --from=builder_ffmpeg /ffmpeg /usr/bin/ffmpeg
COPY --from=builder_ffmpeg /ffprobe /usr/bin/ffprobe
COPY . .

CMD ["python", "-m", "getter"]
