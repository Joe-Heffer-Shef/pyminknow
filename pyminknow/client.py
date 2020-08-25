import argparse
import logging
import warnings

import grpc
import google.protobuf.wrappers_pb2

import minknow.rpc.device_pb2
import minknow.rpc.device_pb2_grpc
import minknow.rpc.manager_pb2
import minknow.rpc.manager_pb2_grpc
import minknow.rpc.protocol_pb2
import minknow.rpc.protocol_pb2_grpc
import minknow.rpc.acquisition_pb2
import minknow.rpc.acquisition_pb2_grpc

import pyminknow.config

LOGGER = logging.getLogger(__name__)

DESCRIPTION = """
This is a client to test a Nanopore gene sequencing device by using its gRPC interface.

Some commands are run against the manager (minKNOW) and some against a device (a mini
"""

USAGE = """
# Assuming we're connecting to the minKNOW, get the port to use for each device
python -m pyminknow.client --list_devices
python -m pyminknow.client --port 8012 --start_protocol sequencing/sequencing_MIN106_DNA:FLO-MIN106:SQK-LSK109:True
"""


class RpcClient:
    """
    Client to send and receive Protocol Buffers objects as part of the minKNOW gRPC interface:

    https://github.com/nanoporetech/minknow_lims_interface/tree/master/minknow/rpc
    """

    # TODO timeouts
    # https://groups.google.com/forum/#!topic/grpc-io/kNBQlQjxQVU

    stub_name = None
    _stub = None

    def __init__(self, channel):
        self.channel = channel

    @staticmethod
    def get_stub(service: str, channel):
        """
        Retrieve the appropriate stub (client) class for the specified service
        """

        # Map services to stubs
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
        """Initialise stub"""

        if not self._stub:
            self._stub = self.get_stub(self.stub_name, self.channel)

        return self._stub


class ManagerClient(RpcClient):
    """
    Manager client

    https://github.com/nanoporetech/minknow_lims_interface/blob/master/minknow/rpc/manager.proto
    """

    stub_name = 'manager'

    def describe_host(self, **kwargs) -> minknow.rpc.manager_pb2.DescribeHostResponse:
        request = minknow.rpc.manager_pb2.DescribeHostRequest()
        return self.stub.describe_host(request, **kwargs)

    def list_devices(self, **kwargs):
        warnings.warn('DEPRECATED: use `flow_cell_positions` instead', DeprecationWarning)

        request = minknow.rpc.manager_pb2.ListDevicesRequest()
        return self.stub.list_devices(request, **kwargs)

    def flow_cell_positions(self, **kwargs) -> iter:
        request = minknow.rpc.manager_pb2.FlowCellPositionsRequest()
        yield from self.stub.flow_cell_positions(request, **kwargs)


class ProtocolClient(RpcClient):
    """
    Protocol client

    https://github.com/nanoporetech/minknow_lims_interface/blob/master/minknow/rpc/protocol.proto
    """

    stub_name = 'protocol'

    def list_protocols(self) -> minknow.rpc.protocol_pb2.ListProtocolsResponse:
        request = minknow.rpc.protocol_pb2.ListProtocolsRequest()
        return self.stub.list_protocols(request)

    def start_protocol(self, identifier: str, user_info: dict = None,
                       args: list = None) -> minknow.rpc.protocol_pb2.StartProtocolResponse:
        """
        :param identifier: Protocol ID
        :param user_info: User input describing the protocol (keys: protocol_group_id, sample_id)
        :param args: The arguments to pass to the protocol
        :returns: StartProtocolResponse(run_id)
        """

        user_info = user_info or dict()

        # StringValue may be null
        _user_info = minknow.rpc.protocol_pb2.ProtocolRunUserInfo(
            protocol_group_id=google.protobuf.wrappers_pb2.StringValue(value=user_info.get('protocol_group_id')),
            sample_id=google.protobuf.wrappers_pb2.StringValue(value=user_info.get('sample_id')),
        )

        request = minknow.rpc.protocol_pb2.StartProtocolRequest(
            identifier=identifier,
            user_info=_user_info,
            args=args,
        )

        return self.stub.start_protocol(request)

    def stop_protocol(self, data_action_on_stop: int):
        """
        Stops the currently running protocol script instance

        data_action_on_stop:
          https://github.com/nanoporetech/minknow_lims_interface/blob/master/minknow/rpc/acquisition.proto#L260
        """
        # >>> minknow.rpc.acquisition_pb2.StopRequest.DataAction.items()
        # [('STOP_DEFAULT', 0), ('STOP_KEEP_ALL_DATA', 1), ('STOP_FINISH_PROCESSING', 2)]
        request = minknow.rpc.protocol_pb2.StopProtocolRequest(data_action_on_stop=data_action_on_stop)
        return self.stub.stop_protocol(request)

    def set_sample_id(self, sample_id: str) -> minknow.rpc.protocol_pb2.SetSampleIdResponse:
        warnings.warn('The sample_id should be set in the request when a protocol starts ( start_protocol() )',
                      DeprecationWarning)
        request = minknow.rpc.protocol_pb2.SetSampleIdRequest(sample_id=sample_id)
        return self.stub.set_sample_id(request)

    def list_protocol_runs(self) -> minknow.rpc.protocol_pb2.ListProtocolRunsResponse:
        request = minknow.rpc.protocol_pb2.ListProtocolRunsRequest()
        return self.stub.list_protocol_runs(request)

    @property
    def latest_run_id(self) -> str:
        return next(iter(self.list_protocol_runs().run_ids))

    def get_run_info(self, run_id: str = None) -> minknow.rpc.protocol_pb2.ProtocolRunInfo:
        # If no run is specified, use the most recent one
        request = minknow.rpc.protocol_pb2.GetRunInfoRequest(run_id=run_id or self.latest_run_id)
        return self.stub.get_run_info(request)

    def wait_for_finished(self, run_id: str, state: int = 0,
                          timeout: int = None) -> minknow.rpc.protocol_pb2.ProtocolRunInfo:
        request = minknow.rpc.protocol_pb2.WaitForFinishedRequest(
            run_id=run_id,
            state=state,
            timeout=timeout,
        )
        return self.stub.wait_for_finished(request)


class DeviceClient(RpcClient):
    """
    Device client

    https://github.com/nanoporetech/minknow_lims_interface/blob/master/minknow/rpc/device.proto
    """

    stub_name = 'device'

    def get_device_state(self) -> minknow.rpc.device_pb2.GetDeviceStateResponse:
        request = minknow.rpc.device_pb2.GetDeviceStateRequest()
        return self.stub.get_device_state(request)

    def get_device_state_name(self) -> str:
        """Get human-readable state"""
        response = self.get_device_state()
        state_name = minknow.rpc.device_pb2.GetDeviceStateResponse.DeviceState.Name(response.device_state)
        LOGGER.debug("Device status: %s => '%s'", response.device_state, state_name)
        return state_name

    def get_device_info(self) -> minknow.rpc.device_pb2.GetDeviceInfoResponse:
        request = minknow.rpc.device_pb2.GetDeviceInfoRequest()
        return self.stub.get_device_info(request)

    def get_flow_cell_info(self) -> minknow.rpc.device_pb2.GetFlowCellInfoResponse:
        request = minknow.rpc.device_pb2.GetFlowCellInfoRequest()
        response = self.stub.get_flow_cell_info(request)
        LOGGER.debug("has_flow_cell: %s", response.has_flow_cell)
        return response


def get_args():
    # TODO separate into separate clients for each service
    parser = argparse.ArgumentParser(usage=USAGE, description=DESCRIPTION)

    parser.add_argument('-v', '--verbose', action='store_true', help='Debug logging')
    parser.add_argument('-o', '--host', default=pyminknow.config.DEFAULT_HOST, help='Connect to this host')
    parser.add_argument('-p', '--port', type=int, default=pyminknow.config.DEFAULT_PORT, help='Connect to this port')
    parser.add_argument('-e', '--describe_host', action='store_true', help='Describe manager host')
    parser.add_argument('-s', '--device_state', action='store_true', help='Get device state')
    parser.add_argument('-q', '--device_info', action='store_true', help='Get device information')
    parser.add_argument('-l', '--list_protocols', action='store_true', help='List available protocols')
    parser.add_argument('-d', '--list_devices', action='store_true', help='List available devices (Manager)')
    parser.add_argument('-w', '--flow_cell_info', action='store_true', help='Get flow cell info (Device)')
    parser.add_argument('-f', '--flow_cell_positions', action='store_true',
                        help='List all known positions where flow cells can be inserted (Manager)')
    parser.add_argument('-i', '--start_protocol', help='Start a protocol given by this identifier')
    parser.add_argument('-g', '--protocol_group_id', help='The group which the experiment should be held in')
    parser.add_argument('-r', '--list_protocol_runs', action='store_true',
                        help='List previously started protocol run IDs, in order of starting')
    parser.add_argument('-u', '--get_run_info', action='store_true', help="Get run info (Protocol)")
    parser.add_argument('-n', '--run_id', help="Protocol run identifier")
    parser.add_argument('-a', '--sample_id', help="Sample identifier")

    return parser, parser.parse_args()


def connect(host: str = 'localhost', port: int = 9501):
    """Connect to the server by opening a gRPC channel"""

    target = '{host}:{port}'.format(host=host, port=port)

    LOGGER.info("Connecting to '%s'...", target)

    # gRPC channel options
    # https://grpc.github.io/grpc/core/group__grpc__arg__keys.html
    options = [
        # ('GRPC_ARG_SERVER_HANDSHAKE_TIMEOUT_MS', 10),
    ]

    channel = grpc.insecure_channel(target=target, options=options)

    return channel


def configure_logging(verbose: bool = False):
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)
    logging.captureWarnings(capture=True)


def main():
    parser, args = get_args()
    configure_logging(verbose=args.verbose)

    with connect(host=args.host, port=args.port) as channel:

        # Device
        if args.device_state or args.device_info or args.flow_cell_info:
            client = DeviceClient(channel)
            if args.device_state:
                print(client.get_device_state())
            elif args.device_info:
                print(client.get_device_info())
            elif args.flow_cell_info:
                print(client.get_flow_cell_info())

            else:
                raise ValueError('Unknown command')

        # Protocol
        elif args.list_protocols or args.start_protocol or args.list_protocol_runs or args.get_run_info:
            client = ProtocolClient(channel)

            if args.list_protocols:
                for protocol in client.list_protocols().protocols:
                    print(protocol)

            elif args.get_run_info:
                print(client.get_run_info(args.run_id))

            # Launch new protocol run
            elif args.start_protocol:
                response = client.start_protocol(
                    identifier=args.start_protocol,
                    user_info=dict(protocol_group_id=args.protocol_group_id, sample_id=args.sample_id),
                    args=[
                        "--fast5=on",
                        "--fast5_data", "trace_table", "fastq", "raw", "zlib_compress",
                        "--base_calling=on",
                        "--fastq=on",
                        "--barcoding_kits", "EXP-NBD114", "EXP-NBD104",
                        "--experiment_time=24"
                    ],
                )
                run_id = response.run_id
                LOGGER.info("Started run ID: %s", run_id)
                run_info = client.get_run_info(run_id)
                print(run_info)
            elif args.list_protocol_runs:
                print(client.list_protocol_runs())
            else:
                raise ValueError('Unknown command')

        # Manager
        elif args.list_devices or args.flow_cell_positions or args.describe_host:

            client = ManagerClient(channel)

            if args.list_devices:
                response = client.list_devices()
                LOGGER.info("Found %s active devices", len(response.active))
                for device in response.active:
                    print(device)

            elif args.describe_host:
                response = client.describe_host()
                print(response)

            elif args.flow_cell_positions:
                for item in client.flow_cell_positions():
                    print(item)

            else:
                raise ValueError('Unknown command')

        else:
            parser.print_help()


if __name__ == '__main__':
    main()
