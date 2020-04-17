"""
Mock minKNOW gRPC client
"""

import argparse
import logging

import grpc

import minknow.rpc.device_pb2
import minknow.rpc.device_pb2_grpc
import minknow.rpc.protocol_pb2
import minknow.rpc.protocol_pb2_grpc
import minknow.rpc.manager_pb2
import minknow.rpc.manager_pb2_grpc

import config

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
    parser.add_argument('-s', '--state', action='store_true', help='Get device state')
    parser.add_argument('-l', '--list_protocols', action='store_true', help='List available protocols')

    return parser, parser.parse_args()


def get_stub(service: str, channel):
    stubs = dict(
        device=minknow.rpc.device_pb2_grpc.DeviceServiceStub,
        protocol=minknow.rpc.protocol_pb2_grpc.ProtocolServiceStub,
        manager=minknow.rpc.manager_pb2_grpc.ManagerServiceStub,
    )

    Stub = stubs[service]

    stub = Stub(channel=channel)

    return stub


def connect(host: str, port: int):
    """
    Connect to the server
    """

    target = '{host}:{port}'.format(host=host, port=port)

    LOGGER.info("Connecting to '%s'...", target)

    channel = grpc.insecure_channel(target=target)

    return channel


def get_device_state(stub):
    request = minknow.rpc.device_pb2.GetDeviceStateRequest()
    response = stub.get_device_state(request)

    state = response.device_state

    # Get human-readable state
    name = minknow.rpc.device_pb2.GetDeviceStateResponse.DeviceState.Name(state)
    LOGGER.info("Device status: '%s'", name)

    return state


def get_run_info_by_id(run_id):
    return


def list_protocols(stub):
    request = minknow.rpc.protocol_pb2.ListProtocolsRequest()
    response = stub.list_protocols(request)

    return response.protocols


def main():
    parser, args = get_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    channel = connect(host=args.host, port=args.port)

    # Device state
    if args.state:
        stub = get_stub('device', channel)
        print(get_device_state(stub))

    # List protocols
    elif args.list_protocols:
        stub = get_stub('protocol', channel)
        print(list_protocols(stub))

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
