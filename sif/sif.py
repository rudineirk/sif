import traceback
from asyncio import Future, Queue, ensure_future, get_event_loop  # noqa
from typing import Any, Dict, List, Optional, Tuple, Union  # noqa

from .data import (  # noqa
    Context,
    Event,
    EventsQueue,
    PubSubMap,
    RpcCall,
    RpcCallQueue,
    RpcMap,
    RpcMethod,
    ServiceMethod,
    Subscription
)
from .exceptions import (
    InvalidListener,
    MethodNotFound,
    TopicNotFound,
    TransportNotFound
)
from .transports import PubSubTransport, RpcTransport  # noqa

RpcFuncMap = Dict[Tuple[str, str], ServiceMethod[Any, Any]]
SubFuncMap = Dict[Tuple[str, str], List[ServiceMethod[Any, Any]]]
RcpTransportMap = Dict[str, RpcTransport]
PubSubTransportMap = Dict[str, PubSubTransport]


async def call_rpc(call: RpcCall, method: ServiceMethod[Any, Any]):
    ctx = Context()
    try:
        ret = await method(call.payload, ctx)
    except Exception as e:
        traceback.print_exc()
        call.fut.set_exception(e)
        return

    call.fut.set_result(ret)


async def call_subscription(event: Event, sub: ServiceMethod[Any, Any]):
    ctx = Context()
    try:
        await sub(event.payload, ctx)
    except:
        traceback.print_exc()


class Sif:
    def __init__(self, service: str) -> None:
        self.loop = get_event_loop()
        self.service = service
        self.rpcs: RpcFuncMap = {}
        self.subs: SubFuncMap = {}
        self.rpcs_decl: RpcMap = {}
        self.subs_decl: PubSubMap = {}
        self.rpc_transports: RcpTransportMap = {}
        self.pubsub_transports: PubSubTransportMap = {}

        self.local_rpc_queue: RpcCallQueue = Queue()
        self.futures: List[Future] = []

    def add_decl(self, decl: Union[RpcMethod, Subscription]) -> None:
        if isinstance(decl, RpcMethod):
            self.rpcs_decl[(decl.service, decl.method)] = decl
            for name in decl.transports:
                if decl.service == self.service:
                    self.rpc_transports[name].add_listener(decl)
                else:
                    self.rpc_transports[name].add_sender(decl)
        else:
            self.subs_decl[(decl.service, decl.topic)] = decl

    def add_rpc_transport(self, name: str, transport: RpcTransport) -> None:
        self.rpc_transports[name] = transport

    def add_pubsub_transport(
        self,
        name: str,
        transport: PubSubTransport,
    ) -> None:
        self.pubsub_transports[name] = transport

    def add_subscriber(
        self,
        decl: Subscription,
        func: ServiceMethod[Any, Any],
    ) -> None:
        key = (decl.service, decl.topic)
        if key not in self.subs:
            self.subs[key] = []

        self.subs[key].append(func)

    def add_rpc_method(
        self,
        decl: RpcMethod,
        func: ServiceMethod[Any, Any],
    ) -> None:
        if decl.service != self.service:
            raise InvalidListener(
                'You cannot listen to a rpc method of another service'
            )
        self.rpcs[(decl.service, decl.method)] = func

    async def call(self, call: RpcCall) -> None:
        try:
            decl = self.rpcs_decl[(call.service, call.method)]
        except KeyError:
            raise MethodNotFound(
                f'service:{call.service} method:{call.method}'
            )
        if call.service == self.service:
            await self.local_rpc_queue.put(call)
            return

        transport = self.get_transport(decl)
        await transport.send_queue.put(call)

    async def push(self, event: Event) -> None:
        try:
            decl = self.subs_decl[(event.service, event.topic)]
        except KeyError:
            raise TopicNotFound(
                f'service:{event.service} topic:{event.topic}'
            )

        transport = self.get_transport(decl)
        await transport.send_queue.put(event)

    def create_rpc_call(
        self,
        service: str,
        method: str,
        payload: Any,
        fut: Optional[Future] = None,
    ) -> RpcCall:
        if fut is None:
            fut = self.loop.create_future()

        return RpcCall(service, method, payload, fut=fut)

    def create_event(
        self,
        service: str,
        topic: str,
        payload: Any,
    ) -> Event:
        return Event(service, topic, payload)

    def get_transport(self, decl: Union[RpcMethod, Subscription]):
        name = decl.transports[0]

        try:
            if isinstance(decl, RpcMethod):
                return self.rpc_transports[name]
            else:
                return self.pubsub_transports[name]
        except KeyError:
            raise TransportNotFound(f'transport: {name}')

    def create_server(self) -> None:
        self.futures.append(ensure_future(self.process_rpc_calls()))
        for transport in self.rpc_transports.values():
            ensure_future(transport.start())

    async def stop(self) -> None:
        await self.local_rpc_queue.put('stop')
        for transport in self.rpc_transports.values():
            await transport.send_queue.put('stop')
            await transport.stop()

        for fut in self.futures:
            try:
                await fut
            except:
                traceback.print_exc()

    async def process_rpc_calls(self) -> None:
        while True:
            try:
                call = await self.local_rpc_queue.get()
            except:
                continue

            if isinstance(call, str):
                if call == 'stop':
                    return
                continue

            try:
                method = self.rpcs[(call.service, call.method)]
            except KeyError:
                raise MethodNotFound(
                    f'service:{call.service} method:{call.method}'
                )

            ensure_future(call_rpc(call, method))

    async def process_events(self, queue: EventsQueue) -> None:
        while True:
            try:
                event = await queue.get()
            except:
                continue

            if isinstance(event, str):
                if event == 'stop':
                    return
                continue

            try:
                subs = self.subs[(event.service, event.topic)]
            except KeyError:
                continue

            for sub in subs:
                ensure_future(call_subscription(event, sub))
