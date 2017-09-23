from asyncio import get_event_loop

from sif import Context

from .deps import greeter, sif


@greeter.greet.listen
async def greet(payload: str, ctx: Context) -> str:
    return 'Hello ' + payload


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
