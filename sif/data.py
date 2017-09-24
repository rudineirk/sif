from asyncio import Future
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    NamedTuple,
    Optional,
    Tuple,
    TypeVar,
    Union
)

EntryType = TypeVar('EntryType')
RetType = TypeVar('RetType')
Serializer = Callable[[EntryType], RetType]
Deserializer = Callable[[EntryType], RetType]


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
    transport: Union[str, List[str]]
    req_serializer: Optional[Serializer[Any, Any]] = None
    req_deserializer: Optional[Deserializer[Any, Any]] = None
    resp_serializer: Optional[Serializer[Any, Any]] = None
    resp_deserializer: Optional[Deserializer[Any, Any]] = None


class Subscription(NamedTuple):
    service: str
    topic: str
    transport: Union[str, List[str]]
    serializer: Optional[Serializer[Any, Any]] = None
    deserializer: Optional[Deserializer[Any, Any]] = None


Payload = TypeVar('Payload')
Resp = TypeVar('Resp')
ServiceMethod = Callable[[Payload, Context], Awaitable[Resp]]
RpcMap = Dict[Tuple[str, str], RpcMethod]
PubSubMap = Dict[Tuple[str, str], Subscription]
