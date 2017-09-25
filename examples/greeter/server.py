from asyncio import get_event_loop

from sif import Context, Sif
from sif_nats import Nats, SifNatsRpc

from .deps import GreeterStub

nats = Nats()
sif = Sif('greeter.server')
sif.add_rpc_transport('nats', SifNatsRpc(sif, nats))
greeter = GreeterStub(sif)


@greeter.greet.listen
async def greet(payload: str, ctx: Context) -> str:
    return 'Hello ' + payload


def main():
    loop = get_event_loop()
    sif.create_server()
    loop.run_forever()


if __name__ == '__main__':
    main()
