from asyncio import get_event_loop
from typing import Awaitable, Generic, List, Optional, TypeVar, Union

from .data import RpcMethod as RpcMethodDecl
from .data import Subscription as SubscriptionDecl
from .data import Deserializer, Event, RpcCall, Serializer, ServiceMethod

EventPayload = TypeVar('EventPayload')
RpcReqPayload = TypeVar('RpcReqPayload')
RpcRespPayload = TypeVar('RpcRespPayload')


class Stub:
    service = ''

    def __init__(self, sif) -> None:
        self.sif = sif


class Rpc(Generic[RpcReqPayload, RpcRespPayload]):
    def __init__(
        self,
        stub: Stub,
        method: str,
        transport: Union[str, List[str]],
        req_serializer: Optional[Serializer]=None,
        req_deserializer: Optional[Deserializer]=None,
        resp_serializer: Optional[Serializer]=None,
        resp_deserializer: Optional[Deserializer]=None,
    ) -> None:
        self.loop = get_event_loop()
        self.stub = stub
        self.sif = stub.sif
        self.service = stub.service
        self.method = method
        self.transport = transport
        self.decl = RpcMethodDecl(
            self.service,
            self.method,
            self.transport,
            req_serializer=req_serializer,
            req_deserializer=req_deserializer,
            resp_serializer=resp_serializer,
            resp_deserializer=resp_deserializer,
        )
        self.sif.add_decl(self.decl)

    def __call__(self, payload: RpcReqPayload) -> Awaitable[RpcRespPayload]:
        return self.call(payload)

    async def call(self, payload: RpcReqPayload) -> RpcRespPayload:
        call = RpcCall(
            self.service,
            self.method,
            payload,
            self.loop.create_future(),
        )
        self.sif.enqueue_rpc_call(call)
        return await call.fut

    def listen(
        self,
        func: ServiceMethod[RpcReqPayload, RpcRespPayload],
    ) -> None:
        self.sif.add_rpc_method(self.decl, func)


class Sub(Generic[EventPayload]):
    def __init__(
        self,
        stub: Stub,
        topic: str,
        transport: Union[str, List[str]],
        serializer: Optional[Serializer]=None,
        deserializer: Optional[Deserializer]=None
    ) -> None:
        self.stub = stub
        self.sif = stub.sif
        self.service = stub.service
        self.topic = topic
        self.transport = transport
        self.decl = SubscriptionDecl(
            self.service,
            self.topic,
            self.transport,
            serializer=serializer,
            deserializer=deserializer,
        )
        self.sif.add_decl(self.decl)

    def __call__(self, payload: EventPayload) -> Awaitable[None]:
        return self.call(payload)

    async def call(self, payload: EventPayload) -> None:
        event = Event(self.service, self.topic, payload)
        await self.sif.push(event)

    def listen(self, func: ServiceMethod[EventPayload, None]):
        self.sif.add_subscriber(self.decl, func)
