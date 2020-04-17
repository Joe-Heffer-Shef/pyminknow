"""
Mock minKNOW gRPC client
"""

import argparse
import logging

import grpc

import config
import minknow.rpc.device_pb2
import minknow.rpc.device_pb2_grpc
import minknow.rpc.manager_pb2
import minknow.rpc.manager_pb2_grpc
import minknow.rpc.protocol_pb2
import minknow.rpc.protocol_pb2_grpc

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
    parser.add_argument('-s', '--device_state', action='store_true', help='Get device state')
    parser.add_argument('-l', '--list_protocols', action='store_true', help='List available protocols')
    parser.add_argument('-d', '--list_devices', action='store_true', help='List available devices')

    return parser, parser.parse_args()


def connect(host: str, port: int):
    """
    Connect to the server
    """

    target = '{host}:{port}'.format(host=host, port=port)

    LOGGER.info("Connecting to '%s'...", target)

    channel = grpc.insecure_channel(target=target)

    return channel


class RpcClient:
    stub_name = None
    _stub = None

    def __init__(self, channel):
        self.channel = channel

    @staticmethod
    def get_stub(service: str, channel):
        stubs = dict(
            device=minknow.rpc.device_pb2_grpc.DeviceServiceStub,
            protocol=minknow.rpc.protocol_pb2_grpc.ProtocolServiceStub,
            manager=minknow.rpc.manager_pb2_grpc.ManagerServiceStub,
        )

        Stub = stubs[service]

        stub = Stub(channel=channel)

        return stub

    @property
    def stub(self):
        if not self._stub:
            self._stub = self.get_stub(self.stub_name, self.channel)

        return self._stub


class ManagerClient(RpcClient):
    stub_name = 'manager'

    def get_run_info_by_id(self, run_id):
        raise NotImplementedError

    def list_devices(self):
        request = minknow.rpc.manager_pb2.ListDevicesRequest()
        response = self.stub.list_devices(request)

        return response


class ProtocolClient(RpcClient):
    stub_name = 'protocol'

    def list_protocols(self):
        request = minknow.rpc.protocol_pb2.ListProtocolsRequest()
        response = self.stub.list_protocols(request)

        return response.protocols


class DeviceClient(RpcClient):
    stub_name = 'device'

    def get_device_state(self):
        request = minknow.rpc.device_pb2.GetDeviceStateRequest()
        response = self.stub.get_device_state(request)

        state = response.device_state

        # Get human-readable state
        name = minknow.rpc.device_pb2.GetDeviceStateResponse.DeviceState.Name(state)
        LOGGER.info("Device status: '%s'", name)

        return state


def main():
    parser, args = get_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    with connect(host=args.host, port=args.port) as channel:

        # Device state
        if args.device_state:
            client = DeviceClient(channel)
            print(client.get_device_state())

        # List protocols
        elif args.list_protocols:
            client = ProtocolClient(channel)
            print(client.list_protocols())

        elif args.list_devices:
            client = ManagerClient(channel)
            devices = client.list_devices()

            LOGGER.info("Found %s active devices", len(devices.active))
            for device in devices.active:
                print(device)

        else:
            parser.print_help()


if __name__ == '__main__':
    main()
