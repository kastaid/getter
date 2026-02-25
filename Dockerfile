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

FROM debian:trixie-slim AS builder_chrome
ARG CHROME_VERSION=124.0.6367.207
RUN set -eux && \
    apt-get -qqy update && \
    apt-get -qqy install --no-install-recommends \
        curl \
        ca-certificates \
        unzip && \
    curl -sS https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chrome-linux64.zip -o chrome.zip && \
    unzip -qq chrome.zip && \
    install -m 0755 chrome-linux64/chrome /usr/bin/google-chrome && \
    curl -sS https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chromedriver-linux64.zip -o chromedriver.zip && \
    unzip -qq chromedriver.zip && \
    install -m 0755 chromedriver-linux64/chromedriver /usr/bin/chromedriver

FROM python:3.12-slim-trixie
ENV PATH=/opt/venv/bin:/app/bin:$PATH \
    CHROME_BIN=/usr/bin/google-chrome
WORKDIR /app
COPY .config/fontconfig/fonts.conf /etc/fonts/local.conf
RUN set -eux && \
    apt-get -qqy update && \
    apt-get -qqy install --no-install-recommends \
        git \
        ca-certificates \
        fonts-roboto \
        fonts-noto-color-emoji \
        cairosvg \
        libjpeg-dev \
        libpng-dev \
        libgtk-3-0 \
        xdg-utils \
        libnss3 \
        libasound2 && \
    rm -rf -- /var/lib/apt/lists/* /var/cache/apt/archives/* /usr/share/man/* /usr/share/doc/* /tmp/* /var/tmp/*

COPY --from=builder_venv /opt/venv /opt/venv
COPY --from=builder_ffmpeg /ffmpeg /usr/bin/ffmpeg
COPY --from=builder_ffmpeg /ffprobe /usr/bin/ffprobe
COPY --from=builder_chrome /usr/bin/google-chrome /usr/bin/google-chrome
COPY --from=builder_chrome /usr/bin/chromedriver /usr/bin/chromedriver
COPY . .

CMD ["python", "-m", "getter"]
