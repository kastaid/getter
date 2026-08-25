# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

import logging
import socket
from typing import TYPE_CHECKING

from telethon.network.connection.tcpabridged import ConnectionTcpAbridged

if TYPE_CHECKING:
    import asyncio
    import ssl as ssl_mod

log = logging.getLogger(__name__)


def _tune(
    sock: socket.socket,
    nodelay: bool,
    keepalive_idle: int,
    keepalive_intvl: int,
    keepalive_cnt: int,
    rcvbuf: int | None = None,
    sndbuf: int | None = None,
) -> None:
    try:
        if nodelay:
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        if hasattr(socket, "TCP_KEEPIDLE"):
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, keepalive_idle)
        if hasattr(socket, "TCP_KEEPINTVL"):
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, keepalive_intvl)
        if hasattr(socket, "TCP_KEEPCNT"):
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, keepalive_cnt)
        if rcvbuf is not None:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, rcvbuf)
        if sndbuf is not None:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, sndbuf)
    except Exception as e:
        log.warning("Could not fully tune socket: %s %s", type(e).__name__, e)


def _get_writer_socket(writer: asyncio.StreamWriter) -> socket.socket | None:
    transport = writer.transport
    if transport is None:
        return None
    return transport.get_extra_info("socket")


class FastTCP(ConnectionTcpAbridged):
    _NODELAY = True
    _KEEPALIVE_IDLE = 10
    _KEEPALIVE_INTVL = 3
    _KEEPALIVE_CNT = 3
    _RCVBUF: int | None = None
    _SNDBUF: int | None = None

    async def _connect(
        self,
        timeout: float | None = None,
        ssl: bool | ssl_mod.SSLContext | None = None,
    ) -> None:
        await super()._connect(timeout=timeout, ssl=ssl)
        self._tune_socket()

    def _tune_socket(self) -> None:
        if self._writer is None:
            return
        sock = _get_writer_socket(self._writer)
        if sock is None:
            return
        _tune(
            sock,
            nodelay=self._NODELAY,
            keepalive_idle=self._KEEPALIVE_IDLE,
            keepalive_intvl=self._KEEPALIVE_INTVL,
            keepalive_cnt=self._KEEPALIVE_CNT,
            rcvbuf=self._RCVBUF,
            sndbuf=self._SNDBUF,
        )


class MediaTCP(FastTCP):
    _NODELAY = False
    _KEEPALIVE_IDLE = 30
    _KEEPALIVE_INTVL = 10
    _KEEPALIVE_CNT = 4
    _RCVBUF = 512 * 1024
    _SNDBUF = 512 * 1024
