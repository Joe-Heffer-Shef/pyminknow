"""
Mock minKNOW gRPC server
"""

import argparse
import logging
import concurrent.futures

import grpc

import service.device

LOGGER = logging.getLogger(__name__)

DESCRIPTION = """
TODO
"""

USAGE = """
TODO
"""

DEFAULT_PORT = 50051
SHUTDOWN_GRACE_PERIOD = 5  # seconds


def get_args():
    parser = argparse.ArgumentParser(usage=USAGE, description=DESCRIPTION)

    parser.add_argument('-v', '--verbose', action='store_true', help='Debug logging')
    parser.add_argument('-p', '--port', type=int, default=DEFAULT_PORT, help='Listen on this port')

    return parser.parse_args()


def serve(port: int):
    thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=10)
    server = grpc.server(thread_pool)

    servicer = service.device.DeviceService()

    servicer.map_to_server(server)

    server.add_insecure_port('[::]:{port}'.format(port=port))

    LOGGER.info("Starting service...")

    try:
        server.start()
        server.wait_for_termination()
    except KeyboardInterrupt:
        LOGGER.info('Stopping server...')
        server.stop(grace=SHUTDOWN_GRACE_PERIOD)

    LOGGER.info("Server stopped.")


def main():
    args = get_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    serve(port=args.port)


if __name__ == '__main__':
    main()
