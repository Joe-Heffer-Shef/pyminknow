"""
Mock minKNOW gRPC client
"""

import argparse
import logging

import grpc

import config
import minknow.rpc.device_pb2_grpc

LOGGER = logging.getLogger(__name__)

DESCRIPTION = """
TODO
"""

USAGE = """
TODO
"""


def get_args():
    parser = argparse.ArgumentParser(usage=USAGE, description=DESCRIPTION)

    parser.add_argument('-v', '--verbose', action='store_true', help='Debug logging')
    parser.add_argument('-o', '--host', type=int, default=config.DEFAULT_HOST, help='Connect to this host')
    parser.add_argument('-p', '--port', type=int, default=config.DEFAULT_PORT, help='Connect to this port')

    return parser.parse_args()


def connect(host: str, port: int):
    """
    Connect to the server and initialise client
    """

    target = '{host}:{port}'.format(host=host, port=port)
    channel = grpc.insecure_channel(target=target)

    stub = minknow.rpc.device_pb2_grpc.DeviceServiceStub(channel=channel)

    return stub


def run(stub):
    state = stub.get_device_state()

    print(state)


def main():
    args = get_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    stub = connect(host=args.host, port=args.port)
    run(stub)


if __name__ == '__main__':
    main()
