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
    PATH=/opt/venv/bin:/app/bin:$PATH

WORKDIR /app
COPY . .

RUN set -ex \
    && apt-get -qqy update \
    && apt-get -qqy install --no-install-recommends \
        tini \
        gnupg2 \
        git \
        locales \
        tzdata \
        build-essential \
    && localedef --quiet -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8 \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
    && dpkg-reconfigure --force -f noninteractive tzdata >/dev/null 2>&1 \
    && python3 -m venv $VIRTUAL_ENV \
    && pip3 install --disable-pip-version-check --default-timeout=100 -r requirements.txt \
    && apt-get -qqy purge --auto-remove \
        build-essential \
    && apt-get -qqy clean \
    && rm -rf -- /var/lib/apt/lists/* /var/cache/apt/archives/* /etc/apt/sources.list.d/* /usr/share/man/* /usr/share/doc/* /var/log/* /tmp/* /var/tmp/*

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["python3", "-m", "getter"]
