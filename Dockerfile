# getter < https://t.me/kastaid >
# Copyright (C) 2022 - kastaid
# All rights reserved.
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in;
# < https://www.github.com/kastaid/getter/blob/main/LICENSE/ >
# ================================================================

FROM python:3.10-slim-bullseye

ENV TEAM=kasta \
    PROJECT=getter \
    TZ=Asia/Jakarta \
    TERM=xterm-256color \
    DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1

RUN set -ex \
    && apt-get -qq update \
    && apt-get -qq -y install --no-install-recommends \
        sudo \
        bash \
        curl \
        wget \
        git \
        gnupg2 \
        tree \
        neofetch \
        fonts-roboto \
        fonts-hack-ttf \
        fonts-noto-color-emoji \
        locales \
        tzdata \
        unzip \
        apt-utils \
        build-essential \
    && localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8 \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
    && dpkg-reconfigure --force -f noninteractive tzdata \
    && groupadd -g 1000 $TEAM \
    && useradd -u 1000 -ms /bin/bash -g $TEAM $TEAM \
    && echo "$TEAM ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/$TEAM \
    && chmod 0440 /etc/sudoers.d/$TEAM \
    && mkdir -p /home/$TEAM/$PROJECT/bin \
    && chmod 777 /home/$TEAM/$PROJECT \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && apt-get -qq update \
    && apt-get -qq -y install google-chrome-stable \
    && wget -N https://chromedriver.storage.googleapis.com/$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE)/chromedriver_linux64.zip -P ~/ \
    && unzip ~/chromedriver_linux64.zip -d ~/ \
    && rm ~/chromedriver_linux64.zip \
    && mv -f ~/chromedriver /usr/bin/chromedriver \
    && chown root:root /usr/bin/chromedriver \
    && chmod 0755 /usr/bin/chromedriver

COPY .config /home/$TEAM
COPY --chown=$TEAM:$TEAM . /home/$TEAM/$PROJECT
WORKDIR /home/$TEAM/$PROJECT
USER $TEAM
ENV VIRTUAL_ENV=/home/$TEAM/venv
ENV PATH $VIRTUAL_ENV/bin:/home/$TEAM/.local/bin:/home/$TEAM/$PROJECT/bin:$PATH

RUN set -ex \
    && python3 -m pip install -U pip \
    && python3 -m venv $VIRTUAL_ENV \
    && pip3 install --no-cache-dir -r requirements.txt \
    && shopt -s extglob \
    && sudo -- sh -c "apt-get -qq -y purge --auto-remove apt-utils build-essential; apt-get -qq -y clean; rm -rf -- /home/$TEAM/.cache /root/.cache /var/lib/apt/lists/* /var/cache/apt/archives/* /etc/apt/sources.list.d/* /usr/share/man/* /usr/share/doc/* /var/log/* /tmp/* /var/tmp/* /etc/sudoers.d/$TEAM"

CMD ["python3", "-m", "getter"]
