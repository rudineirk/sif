from nats.aio.client import Client as NATS

from .data import NatsOpts


class Nats:
    def __init__(self, options: NatsOpts = None) -> None:
        self.nats = NATS()
        self.opts = options
        self.running = False

    async def start(self):
        if self.running:
            return

        self.running = True
        if self.opts is None:
            await self.nats.connect()
            return

        await self.nats.connect(
            servers=self.opts.servers,
            io_loop=self.opts.io_loop,
            error_cb=self.opts.error_cb,
            disconnected_cb=self.opts.disconnected_cb,
            closed_cb=self.opts.closed_cb,
            reconnected_cb=self.opts.reconnected_cb,
            name=self.opts.name,
            pedantic=self.opts.pedantic,
            verbose=self.opts.verbose,
            allow_reconnect=self.opts.allow_reconnect,
            dont_randomize=self.opts.dont_randomize,
            reconnect_time_wait=self.opts.reconnect_time_wait,
            max_reconnect_attempts=self.opts.max_reconnect_attempts,
            ping_interval=self.opts.ping_interval,
            max_outstanding_pings=self.opts.max_outstanding_pings,
            flusher_queue_size=self.opts.flusher_queue_size,
            tls=self.opts.tls,
        )

    async def stop(self):
        if not self.running:
            return

        self.running = False
        await self.nats.close()
