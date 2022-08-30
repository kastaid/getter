# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

FROM python:3.10-slim-bullseye

ENV PROJECT=getter \
    TZ=Asia/Jakarta \
    TERM=xterm-256color \
    DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    VIRTUAL_ENV=/home/app/venv \
    CHROME_BIN=/usr/bin/google-chrome

RUN set -ex \
    && apt-get -qqy update \
    && apt-get -qqy install --no-install-recommends \
        sudo \
        bash \
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
        libjpeg-dev \
        libpng-dev \
        unzip \
        apt-utils \
        build-essential \
    && localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8 \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
    && dpkg-reconfigure --force -f noninteractive tzdata \
    && groupadd -g 1000 app \
    && useradd -u 1000 -ms /bin/bash -g app app \
    && echo "app ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/app \
    && chmod 0440 /etc/sudoers.d/app \
    && mkdir -p /home/app/$PROJECT/bin \
    && chmod 777 /home/app/$PROJECT \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && apt-get -qqy update \
    && apt-get -qqy install google-chrome-stable \
    && wget -N https://chromedriver.storage.googleapis.com/$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE)/chromedriver_linux64.zip -P ~/ \
    && unzip ~/chromedriver_linux64.zip -d ~/ \
    && rm ~/chromedriver_linux64.zip \
    && mv -f ~/chromedriver /usr/bin/chromedriver \
    && chown root:root /usr/bin/chromedriver \
    && chmod 0755 /usr/bin/chromedriver

COPY --chown=app:app . /home/app/$PROJECT
WORKDIR /home/app/$PROJECT
USER app
ENV PATH=$VIRTUAL_ENV/bin:/home/app/.local/bin:/home/app/$PROJECT/bin:$PATH \
    DISPLAY=:99

RUN set -ex \
    && python3 -m pip install -U pip \
    && python3 -m venv $VIRTUAL_ENV \
    && pip3 install --no-cache-dir -r requirements.txt \
    && sudo -- sh -c "apt-get -qqy purge --auto-remove tzdata unzip apt-utils build-essential; apt-get -qqy clean; rm -rf -- /home/app/.cache /root/.cache /var/lib/apt/lists/* /var/cache/apt/archives/* /etc/apt/sources.list.d/* /usr/share/man/* /usr/share/doc/* /var/log/* /tmp/* /var/tmp/* /etc/sudoers.d/app"

CMD ["python3", "-m", "getter"]
