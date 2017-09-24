from sif import Sif, stub  # noqa

SERVICE = 'greeter'


class GreeterStub(stub.Stub):
    service = SERVICE

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.greet: stub.Rpc[str, str] = stub.Rpc(self, 'Greet', '')


sif = Sif(SERVICE)
greeter = GreeterStub(sif)
