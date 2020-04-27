import concurrent.futures
import logging

import grpc

import pyminknow.service.device
import pyminknow.service.manager
import pyminknow.service.protocol

LOGGER = logging.getLogger(__name__)


class Server:
    SERVICES = {
        pyminknow.service.device.DeviceService,
        pyminknow.service.protocol.ProtocolService,
        pyminknow.service.manager.ManagerService,
    }

    def __init__(self, port: int):
        self.port = port
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=10)
        self.server = grpc.server(self.thread_pool)
        self.server.add_insecure_port('[::]:{port}'.format(port=port))

        # Register services
        for Service in self.SERVICES:
            servicer = Service()
            servicer.add_to_server(self.server)
            LOGGER.info('Registered %s', Service.__name__)

    def start(self):
        self.server.start()

    def stop(self, grace: float):
        self.server.stop(grace=grace)

    def wait(self):
        self.server.wait_for_termination()

    def serve(self, grace: float):
        """Run the server"""

        try:
            self.start()
            LOGGER.info("Listening on port %s", self.port)
            self.wait()
        except KeyboardInterrupt:
            LOGGER.info('Stopping server...')
            self.stop(grace=grace)

        LOGGER.info("Server stopped")
