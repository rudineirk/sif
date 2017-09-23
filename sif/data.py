from asyncio import Future
from typing import Any, Callable, NamedTuple, Optional, TypeVar

ServiceMethod = Callable[[Any, 'Context'], Any]

EventSerialized = TypeVar('EventSerialized')
EventDeserialized = TypeVar('EventDeserialized')
EventSerializer = Callable[[EventDeserialized], EventSerialized]
EventDeserializer = Callable[[EventSerialized], EventDeserialized]

RpcReqSerialized = TypeVar('RpcReqSerialized')
RpcReqDeserialized = TypeVar('RpcReqDeserialized')
RpcReqSerializer = Callable[[RpcReqDeserialized], RpcReqSerialized]
RpcReqDeserializer = Callable[[RpcReqSerialized], RpcReqDeserialized]

RpcRespSerialized = TypeVar('RpcRespSerialized')
RpcRespDeserialized = TypeVar('RpcRespDeserialized')
RpcRespSerializer = Callable[[RpcRespDeserialized], RpcRespSerialized]
RpcRespDeserializer = Callable[[RpcRespSerialized], RpcRespDeserialized]


class Context(NamedTuple):
    pass


class RpcCall(NamedTuple):
    service: str
    method: str
    payload: Any
    fut: Future


class Event(NamedTuple):
    service: str
    topic: str
    payload: Any


class RpcMethod(NamedTuple):
    service: str
    method: str
    req_serializer: Optional[RpcReqSerializer[Any, Any]] = None
    req_deserializer: Optional[RpcReqDeserializer[Any, Any]] = None
    resp_serializer: Optional[RpcRespSerializer[Any, Any]] = None
    resp_deserializer: Optional[RpcRespDeserializer[Any, Any]] = None


class Subscription(NamedTuple):
    service: str
    topic: str
    serializer: Optional[EventSerializer[Any, Any]] = None
    deserializer: Optional[EventDeserializer[Any, Any]] = None
