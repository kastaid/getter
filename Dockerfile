# getter < https://t.me/kastaid >
# Copyright (C) 2022-present kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# Please read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

FROM python:3.12-slim-bookworm

ENV TZ=Asia/Jakarta \
    DEBIAN_FRONTEND=noninteractive \
    VIRTUAL_ENV=/opt/venv \
    PATH=/opt/venv/bin:/app/bin:$PATH \
    CHROME_BIN=/usr/bin/google-chrome \
    DISPLAY=:99
ARG LANG=en_US

WORKDIR /app
COPY requirements.txt /tmp/
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
        locales \
        tzdata \
        ffmpeg \
        cairosvg \
        libjpeg-dev \
        libpng-dev \
        libnss3 \
        jq \
        unzip \
        build-essential && \
    localedef --quiet -i ${LANG} -c -f UTF-8 -A /usr/share/locale/locale.alias ${LANG}.UTF-8 && \
    cp /usr/share/zoneinfo/${TZ} /etc/localtime && \
    echo "${TZ}" > /etc/timezone && \
    dpkg-reconfigure --force -f noninteractive tzdata >/dev/null 2>&1 && \
    install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /etc/apt/keyrings/google-chrome.gpg && \
    chmod a+r /etc/apt/keyrings/google-chrome.gpg && \
    echo "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | tee /etc/apt/sources.list.d/google-chrome.list > /dev/null && \
    apt-get -qqy update && \
    apt-get -qqy install --no-install-recommends google-chrome-stable && \
    CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+') && \
    DRIVER_VERSION=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json \
        | jq -r --arg ver "$CHROME_VERSION" '.channels.Stable.versions[] | select(.version | startswith($ver)) | .version' | head -n1) && \
    echo "Using ChromeDriver version: $DRIVER_VERSION" && \
    curl -sS -o /tmp/chromedriver.zip https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${DRIVER_VERSION}/linux64/chromedriver-linux64.zip && \
    unzip -qq /tmp/chromedriver.zip -d /tmp/ && \
    mv /tmp/chromedriver-linux64/chromedriver /usr/bin/chromedriver && \
    chmod +x /usr/bin/chromedriver && \
    command -v chromedriver && \
    $(command -v chromedriver) --version && \
    cp -rf .config ~/ && \
    python -m venv $VIRTUAL_ENV && \
    $VIRTUAL_ENV/bin/pip install --upgrade pip && \
    $VIRTUAL_ENV/bin/pip install --no-cache-dir --disable-pip-version-check --default-timeout=100 -r /tmp/requirements.txt && \
    apt-get -qqy purge --auto-remove \
        locales \
        jq \
        unzip \
        build-essential && \
    apt-get -qqy clean && \
    rm -rf -- /var/lib/apt/lists/* /var/cache/apt/archives/* /etc/apt/sources.list.d/* /usr/share/man/* /usr/share/doc/* /tmp/* /var/tmp/*

COPY . .

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["python", "-m", "getter"]
