import logging
import warnings

import minknow.rpc.device_pb2
import minknow.rpc.device_pb2_grpc
import minknow.rpc.manager_pb2
import minknow.rpc.manager_pb2_grpc
import minknow.rpc.protocol_pb2
import minknow.rpc.protocol_pb2_grpc

LOGGER = logging.getLogger(__name__)


class RpcClient:
    """
    gRPC client
    """

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
    """

    stub_name = 'manager'

    def list_devices(self):
        warnings.warn('DEPRECATED: use `flow_cell_positions` instead', DeprecationWarning)

        request = minknow.rpc.manager_pb2.ListDevicesRequest()
        return self.stub.list_devices(request)

    def flow_cell_positions(self) -> iter:
        request = minknow.rpc.manager_pb2.FlowCellPositionsRequest()
        for response in self.stub.flow_cell_positions(request):
            yield from response.positions


class ProtocolClient(RpcClient):
    """
    Protocol client
    """

    stub_name = 'protocol'

    def list_protocols(self):
        request = minknow.rpc.protocol_pb2.ListProtocolsRequest()
        return self.stub.list_protocols(request)

    def start_protocol(self, identifier: str, *args):
        request = minknow.rpc.protocol_pb2.StartProtocolRequest(
            identifier=identifier,
            args=args,
        )
        return self.stub.start_protocol(request)

    def list_protocol_runs(self) -> list:
        request = minknow.rpc.protocol_pb2.ListProtocolRunsRequest()
        response = self.stub.list_protocol_runs(request)
        return response.run_ids

    @property
    def latest_run_id(self) -> int:
        return self.list_protocol_runs()[0]

    def get_run_info_by_id(self, run_id: int = None):
        # Get latest run ID
        if run_id is None:
            run_id = self.latest_run_id

        request = minknow.rpc.protocol_pb2.GetRunInfoRequest(run_id=run_id)
        return self.stub.get_run_info(request)


class DeviceClient(RpcClient):
    """
    Device client
    """

    stub_name = 'device'

    def get_device_state(self):
        request = minknow.rpc.device_pb2.GetDeviceStateRequest()
        response = self.stub.get_device_state(request)

        state = minknow.rpc.device_pb2.GetDeviceStateResponse.DeviceState(response.device_state)

        # Get human-readable state
        name = minknow.rpc.device_pb2.GetDeviceStateResponse.DeviceState.Name(state)
        LOGGER.info("Device status: '%s'", name)

        return state
