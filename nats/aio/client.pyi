from asyncio import AbstractEventLoop, Future
from ssl import SSLContext
from typing import Awaitable, Callable, List, Optional

NatsCallback = Optional[Callable[[], Awaitable[None]]]

DEFAULT_MAX_FLUSHER_QUEUE_SIZE: int = ...
DEFAULT_MAX_OUTSTANDING_PINGS: int = ...
DEFAULT_MAX_RECONNECT_ATTEMPTS: int = ...
DEFAULT_PING_INTERVAL: int = ...
DEFAULT_RECONNECT_TIME_WAIT: int = ...


class Msg:
    subject: str
    reply: str
    data: bytes
    sid: int


MsgListener = Callable[[Msg], Awaitable[None]]

class Client:
    def __init__(self) -> None: ...
    async def connect(
        self,
        servers: List[str] = ...,
        io_loop: Optional[AbstractEventLoop] = ...,
        error_cb: NatsCallback = ...,
        disconnected_cb: NatsCallback = ...,
        closed_cb: NatsCallback = ...,
        reconnected_cb: NatsCallback = ...,
        name: Optional[str] = ...,
        pedantic: bool = ...,
        verbose: bool = ...,
        allow_reconnect: bool = ...,
        dont_randomize: bool = ...,
        reconnect_time_wait: int = ...,
        max_reconnect_attempts: int = ...,
        ping_interval: int = ...,
        max_outstanding_pings: int = ...,
        flusher_queue_size: int = ...,
        tls: Optional[SSLContext] = ...,
    ) -> None: ...
    async def close(self) -> None: ...
    async def publish(self, subject: str, payload: bytes) -> None: ...
    async def subscribe(
        self,
        subject: str,
        queue: str = ...,
        cb: Optional[MsgListener] = ...,
        future: Optional[Future] = ...,
        max_msgs: int = ...,
        is_async: bool = ...,
    ) -> int: ...
    async def unsubscribe(self, ssid: int, max_msgs: int = ...) -> None: ...
    async def request(
        self,
        subject: str,
        payload: bytes,
        expected: int = ...,
        cb: Optional[MsgListener] = ...,
    ) -> int: ...
    async def timed_request(
        self,
        subject: str,
        payload: bytes,
        timeout: float = ...,
    ) -> Msg: ...
    async def auto_unsubscribe(self, sid: int, limit: int = ...) -> None: ...
