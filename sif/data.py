from asyncio import Future, Queue
from typing import (
    TYPE_CHECKING,
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
    transports: List[str]
    req_serializer: Optional[Serializer[Any, bytes]] = None
    req_deserializer: Optional[Deserializer[bytes, Any]] = None
    resp_serializer: Optional[Serializer[Any, bytes]] = None
    resp_deserializer: Optional[Deserializer[bytes, Any]] = None


class Subscription(NamedTuple):
    service: str
    topic: str
    transports: List[str]
    serializer: Optional[Serializer[Any, bytes]] = None
    deserializer: Optional[Deserializer[bytes, Any]] = None


if TYPE_CHECKING:
    RpcCallQueue = Queue[Union[RpcCall, str]]
    EventsQueue = Queue[Union[Event, str]]
else:
    RpcCallQueue = 'Queue[Union[RpcCall, str]]'
    EventsQueue = 'Queue[Union[Event, str]]'

Payload = TypeVar('Payload')
Resp = TypeVar('Resp')
ServiceMethod = Callable[[Payload, Context], Awaitable[Resp]]
RpcMap = Dict[Tuple[str, str], RpcMethod]
PubSubMap = Dict[Tuple[str, str], Subscription]
