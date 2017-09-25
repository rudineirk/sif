from asyncio import ensure_future
from typing import Any, Dict

from msgpack import packb, unpackb
from nats.aio.client import Client as NATS
from nats.aio.client import Msg

from sif import RpcCall, RpcMethod, RpcTransport, Sif

from .conn import Nats

MethodsMap = Dict[str, RpcMethod]
ServicesMap = Dict[str, MethodsMap]


def decode_rpc_call(
    sif: Sif,
    payload: bytes,
    methods: MethodsMap,
) -> RpcCall:
    try:
        data = unpackb(payload, encoding='utf8')
        service = data['service']
        method = data['method']
        payload = data['payload']
    except:
        raise ValueError('Invalid msg')

    decl = methods[method]
    if decl.req_deserializer:
        payload = decl.req_deserializer(payload)

    return sif.create_rpc_call(
        service=service,
        method=method,
        payload=payload,
    )


def encode_rpc_response(payload: Any, status: int, decl: RpcMethod) -> bytes:
    if decl.resp_serializer:
        payload = decl.resp_serializer(payload)

    return packb({
        'payload': payload,
        'status': status,
    })


def encode_rpc_call(call: RpcCall, decl: RpcMethod) -> bytes:
    payload = call.payload
    if decl.req_serializer:
        payload = decl.req_serializer(payload)

    return packb({
        'service': call.service,
        'method': call.method,
        'payload': payload,
    })


def decode_rpc_response(payload: bytes, decl: RpcMethod) -> Any:
    data = unpackb(payload, encoding='utf8')
    payload = data['payload']
    if decl.resp_deserializer:
        payload = decl.resp_deserializer(payload)

    return payload


async def create_listener(
    sif: Sif,
    nats: NATS,
    service: str,
    methods: MethodsMap,
) -> None:
    async def listener(msg: Msg) -> None:
        call = decode_rpc_call(sif, msg.data, methods)
        decl = methods[call.method]
        await sif.call(call)
        try:
            resp = await call.fut
            resp = encode_rpc_response(resp, status=200, decl=decl)
        except:
            resp = packb({'payload': 'error', 'status': 500})

        await nats.publish(msg.reply, resp)

    subject = service + '.rpc'
    await nats.subscribe(subject, cb=listener)


class SifNatsRpc(RpcTransport):
    def __init__(
        self,
        sif: Sif,
        conn: Nats,
    ) -> None:
        super().__init__(sif)
        self.conn = conn

    async def start(self) -> None:
        await self.conn.start()
        services: ServicesMap = {}
        for (service, method), decl in self.incoming_rpcs.items():
            if service not in services:
                services[service] = {}

            if method not in services[service]:
                services[service][method] = decl

        for service, methods in services.items():
            await create_listener(
                self.sif,
                self.conn.nats,
                service,
                methods,
            )

        self.sif.futures.append(ensure_future(self.call_processor()))

    async def call_processor(self) -> None:
        while True:
            call = await self.send_queue.get()
            if isinstance(call, str):
                if call == 'stop':
                    return
                continue

            try:
                decl = self.outgoing_rpcs[(call.service, call.method)]
            except KeyError as e:
                continue

            req = encode_rpc_call(call, decl)
            subject = call.service + '.rpc'
            try:
                resp = await self.conn.nats.timed_request(subject, req, .5)
            except Exception as e:
                call.fut.set_exception(e)
                continue

            resp = decode_rpc_response(resp.data, decl)
            call.fut.set_result(resp)

    async def stop(self) -> None:
        await self.conn.stop()
