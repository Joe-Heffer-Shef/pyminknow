"""
Mock minKNOW gRPC client
"""

import argparse
import logging

import grpc

import config
import minknow.rpc.device_pb2
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
    parser.add_argument('-o', '--host', default=config.DEFAULT_HOST, help='Connect to this host')
    parser.add_argument('-p', '--port', type=int, default=config.DEFAULT_PORT, help='Connect to this port')

    return parser.parse_args()


def get_device_stub(channel):
    return minknow.rpc.device_pb2_grpc.DeviceServiceStub(channel=channel)


def connect(host: str, port: int):
    """
    Connect to the server and initialise client
    """

    target = '{host}:{port}'.format(host=host, port=port)

    LOGGER.info("Connecting to '%s'...", target)

    channel = grpc.insecure_channel(target=target)

    stub = get_device_stub(channel)

    return stub


def get_device_state(stub):
    request = minknow.rpc.device_pb2.GetDeviceStateRequest()
    response = stub.get_device_state(request)

    state = response.device_state

    return state


def get_run_info_by_id(run_id):
    return


def run(stub):
    print(get_device_state(stub))


def main():
    args = get_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    stub = connect(host=args.host, port=args.port)
    run(stub)


if __name__ == '__main__':
    main()
