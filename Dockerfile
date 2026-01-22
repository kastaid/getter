# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

FROM python:3.12-slim-bookworm AS builder

ENV DEBIAN_FRONTEND=noninteractive \
    VIRTUAL_ENV=/opt/venv \
    PATH=/opt/venv/bin:$PATH
    
WORKDIR /app
COPY requirements.txt /tmp/

RUN set -eux && \
    apt-get -qqy update && \
    apt-get -qqy install --no-install-recommends \
        build-essential && \
    python -m venv $VIRTUAL_ENV && \
    $VIRTUAL_ENV/bin/pip install --upgrade pip && \
    $VIRTUAL_ENV/bin/pip install --no-cache-dir --disable-pip-version-check --default-timeout=100 -r /tmp/requirements.txt

FROM mwader/static-ffmpeg:7.1.1 AS builder_ffmpeg

FROM debian:bookworm-slim AS builder_chrome

ENV DEBIAN_FRONTEND=noninteractive
ARG CHROME_VERSION=124.0.6367.207

RUN set -eux && \
    apt-get -qqy update && \
    apt-get -qqy install --no-install-recommends \
        curl \
        ca-certificates \
        unzip && \
    curl -sS -o /tmp/chrome.zip https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chrome-linux64.zip && \
    unzip -qq /tmp/chrome.zip -d /opt/ && \
    mv /opt/chrome-linux64/chrome /opt/google-chrome && \
    curl -sS -o /tmp/chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chromedriver-linux64.zip && \
    unzip -qq /tmp/chromedriver.zip -d /opt/ && \
    mv /opt/chromedriver-linux64/chromedriver /opt/chromedriver && \
    chmod +x /opt/google-chrome /opt/chromedriver

FROM python:3.12-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PATH=/opt/venv/bin:/app/bin:$PATH \
    CHROME_BIN=/usr/bin/google-chrome

WORKDIR /app
COPY .config /app/.config

RUN set -eux && \
    apt-get -qqy update && \
    apt-get -qqy install --no-install-recommends \
        tini \
        git \
        ca-certificates \
        tree \
        neofetch \
        fonts-roboto \
        fonts-hack-ttf \
        fonts-noto-color-emoji \
        cairosvg \
        libjpeg-dev \
        libpng-dev \
        libgtk-3-0 \
        xdg-utils \
        libnss3 \
        libasound2 && \
    cp -rf .config ~/ && \
    rm -rf -- /var/lib/apt/lists/* /var/cache/apt/archives/* /usr/share/man/* /usr/share/doc/* /tmp/* /var/tmp/*

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder_ffmpeg /ffmpeg /usr/bin/ffmpeg
COPY --from=builder_ffmpeg /ffprobe /usr/bin/ffprobe
COPY --from=builder_chrome /opt/google-chrome /usr/bin/google-chrome
COPY --from=builder_chrome /opt/chromedriver /usr/bin/chromedriver
COPY . .

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["python", "-m", "getter"]
