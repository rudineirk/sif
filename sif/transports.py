from asyncio import Queue
from typing import TYPE_CHECKING

from .data import (  # noqa
    Event,
    EventsQueue,
    PubSubMap,
    RpcCall,
    RpcCallQueue,
    RpcMap,
    RpcMethod,
    Subscription
)


class RpcTransport:
    def __init__(self, sif: 'Sif') -> None:
        self.sif = sif
        self.incoming_rpcs: RpcMap = {}
        self.outgoing_rpcs: RpcMap = {}
        self.send_queue: RpcCallQueue = Queue()

    def add_listener(self, decl: RpcMethod) -> None:
        self.incoming_rpcs[(decl.service, decl.method)] = decl

    def add_sender(self, decl: RpcMethod) -> None:
        self.outgoing_rpcs[(decl.service, decl.method)] = decl

    async def start(self) -> None:
        raise NotImplementedError

    async def stop(self) -> None:
        raise NotImplementedError


class PubSubTransport:
    def __init__(self, sif: 'Sif') -> None:
        self.sif = sif
        self.incoming_subs: PubSubMap = {}
        self.outgoing_subs: PubSubMap = {}
        self.recv_queue: EventsQueue = Queue()
        self.send_queue: EventsQueue = Queue()

    def add_listener(self, decl: Subscription) -> None:
        self.incoming_subs[(decl.service, decl.topic)] = decl

    def add_sender(self, decl: Subscription) -> None:
        self.outgoing_subs[(decl.service, decl.topic)] = decl

    async def start(self) -> None:
        raise NotImplementedError

    async def stop(self) -> None:
        raise NotImplementedError


if TYPE_CHECKING:
    from .sif import Sif  # noqa
