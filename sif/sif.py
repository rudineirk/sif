import traceback
from asyncio import Queue, ensure_future, get_event_loop
from typing import List, Union  # noqa

from .data import (
    Context,
    Event,
    RpcCall,
    RpcMethod,
    ServiceMethod,
    Subscription
)
from .exceptions import MethodNotFound


async def call_rpc(call: RpcCall, method: ServiceMethod):
    ctx = Context()
    try:
        ret = await method(call.payload, ctx)
    except Exception as e:
        traceback.print_exc()
        call.fut.set_exception(e)
        return

    call.fut.set_result(ret)


async def call_subscription(event: Event, sub: ServiceMethod):
    ctx = Context()
    try:
        await sub(event.payload, ctx)
    except:
        traceback.print_exc()


class Sif:
    def __init__(self, service: str):
        self.loop = get_event_loop()
        self.service = service
        self.rpcs = {}
        self.subscriptions = {}
        self.local_rpc_queue = Queue()
        self.remote_rpc_queue = Queue()
        self.pubsub_send_queue = Queue()
        self.pubsub_receive_queue = Queue()
        self.futures: List[Future] = []
        self.running = True

    def add_decl(self, decl: Union[RpcMethod, Subscription]) -> None:
        if isinstance(decl, RpcMethod):
            self.rpcs[(decl.service, decl.method)] = decl
        else:
            self.subs[(decl.service, decl.topic)] = decl

    def add_subscriber(
        self,
        service: str,
        topic: str,
        func: ServiceMethod,
    ) -> None:
        if topic not in self.subscriptions:
            self.subscriptions[topic] = []

        self.subscriptions[topic].append(func)

    def add_rpc_method(self, method: str, func: ServiceMethod) -> None:
        self.rpcs[method] = func

    def enqueue_rpc_call(self, call: RpcCall) -> None:
        if call.service == self.service:
            self.local_rpc_queue.put_nowait(call)
            return

        self.remote_rpc_queue.put_nowait(call)

    async def push(self, event: Event) -> None:
        await self.pubsub_send_queue.put(event)

    def create_server(self) -> None:
        self.futures.append(ensure_future(self.process_rpc_calls()))
        self.futures.append(ensure_future(self.process_events()))

    async def stop(self) -> None:
        self.running = False
        await self.local_rpc_queue.put('stop')
        await self.pubsub_receive_queue.put('stop')
        for fut in self.futures:
            try:
                await fut
            except:
                traceback.print_exc()

    async def process_rpc_calls(self) -> None:
        while self.running:
            try:
                call = await self.local_rpc_queue.get()
            except:
                continue

            if call == 'stop':
                return

            try:
                method = self.rpcs[call.method]
            except KeyError:
                raise MethodNotFound(call.method)

            ensure_future(call_rpc(call, method))

    async def process_events(self) -> None:
        while self.running:
            try:
                event = await self.pubsub_receive_queue.get()
            except:
                continue

            if event == 'stop':
                return

            try:
                subs = self.subscriptions[event.topic]
            except KeyError:
                continue

            for sub in subs:
                ensure_future(call_subscription, sub)
