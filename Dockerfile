# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

FROM python:3.12-slim-trixie AS builder_venv
ENV VIRTUAL_ENV=/opt/venv \
    PATH=/opt/venv/bin:/root/.local/bin:$PATH
WORKDIR /app
COPY requirements.txt /tmp/
RUN set -eux && \
    apt-get -qqy update && \
    apt-get -qqy install --no-install-recommends \
        build-essential curl && \
    curl -LsSf https://astral.sh/uv/install.sh | sh && \
    python -m venv $VIRTUAL_ENV && \
    uv pip install --python $VIRTUAL_ENV/bin/python -r /tmp/requirements.txt

FROM mwader/static-ffmpeg:7.1.1 AS builder_ffmpeg

FROM python:3.12-slim-trixie
ENV PATH=/opt/venv/bin:/app/bin:$PATH
WORKDIR /app
RUN set -eux && \
    apt-get -qqy update && \
    apt-get -qqy install --no-install-recommends \
        git \
        ca-certificates && \
    rm -rf -- /var/lib/apt/lists/* /var/cache/apt/archives/* /usr/share/man/* /usr/share/doc/* /tmp/* /var/tmp/*

COPY --from=builder_venv /opt/venv /opt/venv
COPY --from=builder_ffmpeg /ffmpeg /usr/bin/ffmpeg
COPY --from=builder_ffmpeg /ffprobe /usr/bin/ffprobe
COPY . .

CMD ["python", "-m", "getter"]
