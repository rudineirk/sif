from sif import Sif, stub  # noqa


class GreeterStub(stub.Stub):
    service = 'greeter.server'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.greet: stub.Rpc[str, str] = stub.Rpc(self, 'Greet', ['nats'])
