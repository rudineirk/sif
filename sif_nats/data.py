from asyncio import AbstractEventLoop
from ssl import SSLContext
from typing import Awaitable, Callable, List, NamedTuple, Optional

from nats.aio.client import (
    DEFAULT_MAX_FLUSHER_QUEUE_SIZE,
    DEFAULT_MAX_OUTSTANDING_PINGS,
    DEFAULT_MAX_RECONNECT_ATTEMPTS,
    DEFAULT_PING_INTERVAL,
    DEFAULT_RECONNECT_TIME_WAIT
)

NatsCallback = Optional[Callable[[], Awaitable[None]]]


class NatsOpts(NamedTuple):
    servers: List[str] = ["nats://127.0.0.1:4222"]
    io_loop: Optional[AbstractEventLoop] = None
    error_cb: NatsCallback = None
    disconnected_cb: NatsCallback = None
    closed_cb: NatsCallback = None
    reconnected_cb: NatsCallback = None
    name: Optional[str] = None
    pedantic: bool = False
    verbose: bool = False
    allow_reconnect: bool = True
    dont_randomize: bool = False
    reconnect_time_wait: int = DEFAULT_RECONNECT_TIME_WAIT
    max_reconnect_attempts: int = DEFAULT_MAX_RECONNECT_ATTEMPTS
    ping_interval: int = DEFAULT_PING_INTERVAL
    max_outstanding_pings: int = DEFAULT_MAX_OUTSTANDING_PINGS
    flusher_queue_size: int = DEFAULT_MAX_FLUSHER_QUEUE_SIZE
    tls: Optional[SSLContext] = None
