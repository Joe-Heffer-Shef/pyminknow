import logging

import minknow_api.manager_pb2
import minknow_api.manager_pb2_grpc

import pyminknow.config

LOGGER = logging.getLogger(__name__)


class ManagerService(minknow_api.manager_pb2_grpc.ManagerServiceServicer):
    """
    Manager service

    https://github.com/nanoporetech/minknow_lims_interface/blob/master/minknow/rpc/manager.proto
    """
    add_to_server = minknow_api.manager_pb2_grpc.add_ManagerServiceServicer_to_server

    def get_version_info(self, request, context):
        return minknow_api.manager_pb2.GetVersionInfoResponse()

    def describe_host(self, request, context):
        return minknow_api.manager_pb2.DescribeHostResponse(
            product_code=pyminknow.config.PRODUCT_CODE,
            description=pyminknow.config.DESCRIPTION,
            serial=pyminknow.config.SERIAL,
            network_name=pyminknow.config.NETWORK_NAME,
        )

    def flow_cell_positions(self, request, context) -> iter:
        """Provides a snapshot of places where users can insert flow cells."""

        positions = self._flow_cell_positions

        yield minknow_api.manager_pb2.FlowCellPositionsResponse(
            total_count=len(positions),
            positions=positions,
        )

    @property
    def _flow_cell_positions(self) -> list:
        state_name = 'STATE_RUNNING'
        state = minknow_api.manager_pb2.FlowCellPosition.State.Value(state_name)

        return [
            minknow_api.manager_pb2.FlowCellPosition(
                name=device['name'],
                location=minknow_api.manager_pb2.FlowCellPosition.Location(**device['layout']),
                state=state,
                rpc_ports=minknow_api.manager_pb2.FlowCellPosition.RpcPorts(**device['ports']),
                error_info='',
            ) for device in pyminknow.config.DEVICES
        ]
