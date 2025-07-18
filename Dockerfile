# getter < https://t.me/kastaid >
# Copyright (C) 2022-present kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# Please read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

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

FROM python:3.12-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PATH=/opt/venv/bin:/app/bin:$PATH \
    CHROME_BIN=/usr/bin/google-chrome \
    DISPLAY=:99
ARG CHROME_VERSION=124.0.6367.207

WORKDIR /app
COPY .config /app/.config

RUN set -eux && \
    apt-get -qqy update && \
    apt-get -qqy install --no-install-recommends \
        tini \
        gnupg2 \
        git \
        curl \
        wget \
        tree \
        neofetch \
        fonts-roboto \
        fonts-hack-ttf \
        fonts-noto-color-emoji \
        ffmpeg \
        cairosvg \
        libjpeg-dev \
        libpng-dev \
        libnss3 \
        libatk1.0-0 \
        libatk-bridge2.0-0 \
        libcups2 \
        libxcomposite1 \
        libxdamage1 \
        libxrandr2 \
        libxcb1 \
        libxext6 \
        libxfixes3 \
        libasound2 \
        libgtk-3-0 \
        xdg-utils \
        ca-certificates \
        unzip && \
    curl -sS -o /tmp/chrome.zip https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chrome-linux64.zip && \
    unzip -qq /tmp/chrome.zip -d /opt/ && \
    mv /opt/chrome-linux64 /opt/chrome && \
    ln -s /opt/chrome/chrome $CHROME_BIN && \
    chmod +x $CHROME_BIN && \
    rm -f /tmp/chrome.zip && \
    curl -sS -o /tmp/chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chromedriver-linux64.zip && \
    unzip -qq /tmp/chromedriver.zip -d /opt/ && \
    mv /opt/chromedriver-linux64/chromedriver /usr/bin/chromedriver && \
    chmod +x /usr/bin/chromedriver && \
    rm -f /tmp/chromedriver.zip && \
    cp -rf .config ~/ && \
    apt-get -qqy purge --auto-remove \
        unzip && \
    rm -rf -- /var/lib/apt/lists/* /var/cache/apt/archives/* /usr/share/man/* /usr/share/doc/* /tmp/* /var/tmp/*

COPY --from=builder /opt/venv /opt/venv
COPY . .

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["python", "-m", "getter"]
