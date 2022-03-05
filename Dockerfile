FROM python:3.10-slim-bullseye

ENV TERM xterm-256color
ENV DEBIAN_FRONTEND noninteractive
ENV PIP_NO_CACHE_DIR 1
ENV TZ Asia/Jakarta

WORKDIR /app
COPY . .

RUN set -ex \
    && apt-get -qq update \
    && apt-get -qq -y install --no-install-recommends git \
        apt-utils \
        build-essential \
        gnupg2 \
        tzdata \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
    && dpkg-reconfigure -f noninteractive tzdata \
    && python3 -m pip install -U pip \
    && pip3 install --no-cache-dir -U -r requirements.txt \
    && apt-get -qq -y purge --auto-remove \
        apt-utils \
        build-essential \
        gnupg2 \
        tzdata \
    && apt-get -qq -y clean \
    && rm -rf -- /var/lib/apt/lists/* /var/cache/apt/archives/* /etc/apt/sources.list.d/* /usr/share/man/* /usr/share/doc/* /var/log/* /tmp/* /var/tmp/* /root/.cache

EXPOSE 80 443

CMD ["python3", "-m", "getter"]
