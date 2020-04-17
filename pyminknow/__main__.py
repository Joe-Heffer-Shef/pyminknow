"""
Mock minKNOW gRPC server
"""

import argparse
import logging
import concurrent.futures

import grpc

import service

LOGGER = logging.getLogger(__name__)

DESCRIPTION = """
TODO
"""

USAGE = """
TODO
"""

DEFAULT_PORT = 50051


def get_args():
    parser = argparse.ArgumentParser(usage=USAGE, description=DESCRIPTION)

    parser.add_argument('-v', '--verbose', action='store_true', help='Debug logging')
    parser.add_argument('-p', '--port', type=int, default=DEFAULT_PORT, help='Listen on this port')

    return parser.parse_args()


def serve(port: int):
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)
    server = grpc.server(executor)

    servicer = service.ManagerServiceServicer()

    servicer.map_to_server(server)

    server.add_insecure_port('[::]:{port}'.format(port=port))

    server.start()


def main():
    args = get_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    serve(port=args.port)


if __name__ == '__main__':
    main()
