from asyncio import get_event_loop

from sif import Sif
from sif_nats import Nats, SifNatsRpc

from .deps import GreeterStub

nats = Nats()
sif = Sif('greeter.client')
sif.add_rpc_transport('nats', SifNatsRpc(sif, nats))
greeter = GreeterStub(sif)


async def run():
    resp = await greeter.greet('Bob')
    print('Resp: ' + resp)


def main():
    loop = get_event_loop()
    sif.create_server()
    loop.run_until_complete(run())
    loop.run_until_complete(sif.stop())


if __name__ == '__main__':
    main()
