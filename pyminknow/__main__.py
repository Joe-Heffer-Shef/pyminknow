import argparse
import logging
import concurrent.futures

import grpc

import config
import service.device
import service.protocol
import service.manager

LOGGER = logging.getLogger(__name__)

DESCRIPTION = """
This service mimics a Nanopore minKNOW gene sequencing device by using its gRPC interface.
"""

USAGE = """
python pyminknow --help
"""

SERVICES = {
    service.device.DeviceService,
    service.protocol.ProtocolService,
    service.manager.ManagerService,
}


def get_args():
    """Command-line arguments"""
    parser = argparse.ArgumentParser(usage=USAGE, description=DESCRIPTION)

    parser.add_argument('-v', '--verbose', action='store_true', help='Debug logging')
    parser.add_argument('-p', '--port', type=int, default=config.DEFAULT_PORT, help='Listen on this port')
    parser.add_argument('-g', '--grace', type=int, default=config.GRACE, help='Grace period (seconds) when stopping')

    return parser.parse_args()


def get_server(port: int):
    thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=10)
    server = grpc.server(thread_pool)
    server.add_insecure_port('[::]:{port}'.format(port=port))

    return server


def serve(port: int, grace: float):
    """Run the server"""

    server = get_server(port=port)

    # Register services
    for Service in SERVICES:
        servicer = Service()
        servicer.add_to_server(server)
        LOGGER.info('Registered %s', Service.__name__)

    try:
        server.start()
        LOGGER.info("Listening on port %s", port)
        server.wait_for_termination()
    except KeyboardInterrupt:
        LOGGER.info('Stopping server...')
        server.stop(grace=grace)

    LOGGER.info("Server stopped.")


def configure_logging(verbose: bool = False):
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)
    logging.captureWarnings(capture=True)


def main():
    args = get_args()
    configure_logging(verbose=args.verbose)

    serve(port=args.port, grace=args.grace)


if __name__ == '__main__':
    main()
