from asyncio import Queue
from typing import TYPE_CHECKING, Union  # noqa

from .data import (  # noqa
    Event,
    PubSubMap,
    RpcCall,
    RpcMap,
    RpcMethod,
    Subscription
)

if TYPE_CHECKING:
    RpcCallQueue = Queue[Union[RpcCall, str]]
    EventsQueue = Queue[Union[Event, str]]
else:
    RpcCallQueue = 'Queue[Union[RpcCall, str]]'
    EventsQueue = 'Queue[Union[Event, str]]'


class RpcTransport:
    def __init__(self) -> None:
        self.incoming_rpcs: RpcMap = {}
        self.outgoing_rpcs: RpcMap = {}
        self.recv_queue: RpcCallQueue = Queue()
        self.send_queue: RpcCallQueue = Queue()

    def add_listener(self, decl: RpcMethod):
        self.incoming_rpcs[(decl.service, decl.method)] = decl

    def add_sender(self, decl: RpcMethod):
        self.outgoing_rpcs[(decl.service, decl.method)] = decl

    async def start(self):
        raise NotImplementedError

    async def stop(self):
        raise NotImplementedError


class PubSubTransport:
    def __init__(self) -> None:
        self.incoming_subs: PubSubMap = {}
        self.outgoing_subs: PubSubMap = {}
        self.recv_queue: EventsQueue = Queue()
        self.send_queue: EventsQueue = Queue()

    def add_listener(self, decl: Subscription):
        self.incoming_subs[(decl.service, decl.topic)] = decl

    def add_sender(self, decl: Subscription):
        self.outgoing_subs[(decl.service, decl.topic)] = decl
