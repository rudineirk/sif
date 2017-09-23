from asyncio import get_event_loop
from typing import Awaitable, Generic, Optional

from .data import RpcMethod as RpcMethodDecl
from .data import Subscription as SubscriptionDecl
from .data import (
    Event,
    EventDeserialized,
    EventDeserializer,
    EventSerialized,
    EventSerializer,
    RpcCall,
    RpcReqDeserialized,
    RpcReqDeserializer,
    RpcReqSerialized,
    RpcReqSerializer,
    RpcRespDeserialized,
    RpcRespDeserializer,
    RpcRespSerialized,
    RpcRespSerializer,
    ServiceMethod
)
from .exceptions import InvalidListener


class Client:
    service = ''

    def __init__(self, sif):
        self.sif = sif


class RpcMethod(Generic[
    RpcReqDeserialized,
    RpcReqSerialized,
    RpcRespDeserialized,
    RpcRespSerialized
]):
    def __init__(
        self,
        client: Client,
        method: str,
        req_serializer: Optional[RpcReqSerializer]=None,
        req_deserializer: Optional[RpcReqDeserializer]=None,
        resp_serializer: Optional[RpcRespSerializer]=None,
        resp_deserializer: Optional[RpcRespDeserializer]=None,
    ):
        self.loop = get_event_loop()
        self.client = client
        self.sif = client.sif
        self.service = client.service
        self.method = method
        self.decl = RpcMethodDecl(
            self.service,
            self.method,
            req_serializer=req_serializer,
            req_deserializer=req_deserializer,
            resp_serializer=resp_serializer,
            resp_deserializer=resp_deserializer,
        )
        self.sif.add_decl(self.decl)

    def __call__(
        self, payload: RpcReqDeserialized
    ) -> Awaitable[RpcRespDeserialized]:
        return self.call(payload)

    async def call(self, payload: RpcReqDeserialized) -> RpcRespDeserialized:
        call = RpcCall(
            self.service,
            self.method,
            payload,
            self.loop.create_future(),
        )
        self.sif.enqueue_rpc_call(call)
        return await call.fut

    def listen(self, func: ServiceMethod) -> None:
        if self.service != self.sif.service:
            raise InvalidListener(
                'You cannot listen to a rpc method of another service'
            )
        self.sif.add_rpc_method(self.method, func)


class Subscription(Generic[EventSerialized, EventDeserialized]):
    def __init__(
        self,
        client: Client,
        topic: str,
        serializer: Optional[EventSerializer]=None,
        deserializer: Optional[EventDeserializer]=None
    ):
        self.client = client
        self.sif = client.sif
        self.service = client.service
        self.topic = topic
        self.decl = SubscriptionDecl(
            self.service,
            self.topic,
            serializer=serializer,
            deserializer=deserializer,
        )
        self.sif.add_decl(self.decl)

    def __call__(self, payload: EventDeserialized) -> Awaitable[None]:
        return self.call(payload)

    async def call(self, payload: EventDeserialized) -> None:
        event = Event(self.service, self.topic, payload)
        await self.sif.push(event)

    def listen(self, func):
        self.sif.add_subscriber(self.topic, func)
