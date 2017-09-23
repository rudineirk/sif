from sif import Sif, client

SERVICE = 'greeter'


class GreeterClient(client.Client):
    service = SERVICE

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.greet = client.RpcMethod(self, 'Greet')


sif = Sif(SERVICE)
greeter = GreeterClient(sif)
