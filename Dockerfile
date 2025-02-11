# getter < https://t.me/kastaid >
# Copyright (C) 2022-present kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# Please read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

FROM python:3.12-slim-bookworm

ENV TZ=Asia/Jakarta \
    TERM=xterm-256color \
    DEBIAN_FRONTEND=noninteractive \
    VIRTUAL_ENV=/opt/venv \
    PATH=/opt/venv/bin:/app/bin:$PATH \
    CHROME_BIN=/usr/bin/google-chrome \
    DISPLAY=:99
ARG LANG=en_US

WORKDIR /app
COPY requirements.txt /tmp/

RUN set -eux \
    && apt-get -qqy update \
    && apt-get -qqy install --no-install-recommends \
        gnupg \
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
        unzip \
        build-essential \
    && localedef --quiet -i ${LANG} -c -f UTF-8 -A /usr/share/locale/locale.alias ${LANG}.UTF-8 \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
    && dpkg-reconfigure --force -f noninteractive tzdata >/dev/null 2>&1 \
    && install -m 0755 -d /etc/apt/keyrings \
    && curl -fsSL https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /etc/apt/keyrings/google-chrome.gpg \
    && chmod a+r /etc/apt/keyrings/google-chrome.gpg \
    && echo "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | tee /etc/apt/sources.list.d/google-chrome.list > /dev/null \
    && apt-get -qqy update \
    && apt-get -qqy install --no-install-recommends google-chrome-stable \
    && wget -qN https://chromedriver.storage.googleapis.com/$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE)/chromedriver_linux64.zip -P ~/ \
    && unzip -qq ~/chromedriver_linux64.zip -d ~/ \
    && rm -rf ~/chromedriver_linux64.zip \
    && mv -f ~/chromedriver /usr/bin/chromedriver \
    && chmod +x /usr/bin/chromedriver \
    && command -v chromedriver \
    && $(command -v chromedriver) --version \
    && cp -rf .config ~/ \
    && python -m venv $VIRTUAL_ENV \
    && $VIRTUAL_ENV/bin/pip install --upgrade pip \
    && $VIRTUAL_ENV/bin/pip install --no-cache-dir --disable-pip-version-check --default-timeout=100 -r /tmp/requirements.txt \
    && apt-get -qqy purge --auto-remove \
        unzip \
        build-essential \
    && apt-get -qqy clean \
    && rm -rf -- /var/lib/apt/lists/* /var/cache/apt/archives/* /etc/apt/sources.list.d/* /usr/share/man/* /usr/share/doc/* /var/log/* /tmp/* /var/tmp/*

COPY . .

CMD ["python", "-m", "getter"]
