import concurrent.futures
import logging

import grpc

import pyminknow.config
import pyminknow.service.device
import pyminknow.service.manager
import pyminknow.service.protocol

LOGGER = logging.getLogger(__name__)

MAX_WORKERS = 100


class Server:
    SERVICES = {
        pyminknow.service.device.DeviceService,
        pyminknow.service.protocol.ProtocolService,
        pyminknow.service.manager.ManagerService,
    }

    def __init__(self, device_port: int):
        self.port = device_port
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS)
        self.servers = list()

        # Create manager service
        server = grpc.server(thread_pool=self.thread_pool)
        server.add_insecure_port('[::]:{port}'.format(port=device_port))
        manager_servicer = pyminknow.service.manager.ManagerService()
        manager_servicer.add_to_server(server)
        self.servers.append(server)

        # Devices
        for device in pyminknow.config.DEVICES:
            device_port = device['ports']['insecure']
            server = grpc.server(thread_pool=self.thread_pool)
            server.add_insecure_port('[::]:{port}'.format(port=device_port))
            pyminknow.service.protocol.ProtocolService(device=device).add_to_server(server)
            device_servicer = pyminknow.service.device.DeviceService(device=device)
            device_servicer.add_to_server(server)
            self.servers.append(server)

            LOGGER.info("Added insecure port %s for device %s", device_port, device['name'])

    def start(self):
        for server in self.servers:
            server.start()
        LOGGER.info("Listening on port %s", self.port)

    def stop(self, grace: float):
        LOGGER.info('Stopping server...')
        for server in self.servers:
            server.stop(grace=grace)
        LOGGER.info("Server stopped")

    def wait(self):
        for server in self.servers:
            server.wait_for_termination()

    def serve(self, grace: float):
        """Run the server"""
        try:
            self.start()
            self.wait()
        except KeyboardInterrupt:
            self.stop(grace=grace)
