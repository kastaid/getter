# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

ARG PYTHON_IMAGE=python3.14-trixie-slim
ARG UV_VERSION=0.12.7
ARG FFMPEG_TAG=autobuild-2026-08-14-13-16
ARG FFMPEG_BUILD=n7.1.5-12-g1fdbca85aa
ARG FFMPEG_VARIANT=linux64-gpl-7.1
FROM debian:trixie-slim AS builder_ffmpeg
ARG FFMPEG_TAG
ARG FFMPEG_BUILD
ARG FFMPEG_VARIANT
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update -qq && apt-get install -qqy --no-install-recommends \
        ca-certificates \
        aria2 \
        xz-utils \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /ffmpeg
RUN --mount=type=cache,target=/ffmpeg/cache,id=ffmpeg-dl \
    ARCHIVE="/ffmpeg/cache/ffmpeg-${FFMPEG_BUILD}-${FFMPEG_VARIANT}.tar.xz" && \
    [ ! -f "$ARCHIVE" ] || xz -t "$ARCHIVE" || rm -f "$ARCHIVE" && \
    aria2c -q -x16 -s16 -k1M \
        --dir=/ffmpeg/cache \
        --out=ffmpeg-${FFMPEG_BUILD}-${FFMPEG_VARIANT}.tar.xz \
        --allow-overwrite=false \
        "https://github.com/BtbN/FFmpeg-Builds/releases/download/${FFMPEG_TAG}/ffmpeg-${FFMPEG_BUILD}-${FFMPEG_VARIANT}.tar.xz" \
    && mkdir /ffmpeg-bin \
    && tar -xf "$ARCHIVE" -C /ffmpeg-bin --strip-components=2 --wildcards "*/bin/ffmpeg" "*/bin/ffprobe"
FROM ghcr.io/astral-sh/uv:${UV_VERSION}-${PYTHON_IMAGE}
ENV TERM=xterm \
    DEBIAN_FRONTEND=noninteractive \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_SYSTEM_PYTHON=1 \
    UV_BREAK_SYSTEM_PACKAGES=1
WORKDIR /app
RUN apt-get update -qq && apt-get install -qqy --no-install-recommends \
        git \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install -qr requirements.txt && \
    python_prefix=/usr/local && \
    python_dir="$python_prefix"/lib/python3.14 && \
    rm -rf \
        "$python_prefix"/bin/pip \
        "$python_prefix"/bin/pip3 \
        "$python_prefix"/bin/pip3.14 \
        "$python_dir"/site-packages/pip \
        "$python_dir"/site-packages/pip-*.dist-info \
        "$python_dir"/ensurepip
COPY . .
COPY --from=builder_ffmpeg /ffmpeg-bin/ /usr/local/bin/
CMD ["python", "-m", "getter"]
