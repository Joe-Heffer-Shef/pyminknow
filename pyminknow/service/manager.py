import logging
import warnings
import random

import minknow.rpc.manager_pb2
import minknow.rpc.manager_pb2_grpc

LOGGER = logging.getLogger(__name__)


class ManagerService(minknow.rpc.manager_pb2_grpc.ManagerServiceServicer):
    """
    Manager service
    """
    add_to_server = minknow.rpc.manager_pb2_grpc.add_ManagerServiceServicer_to_server

    @property
    def active(self) -> list:
        return [
            minknow.rpc.manager_pb2.ListDevicesResponse.ActiveDevice(
                name='MN0000',
                layout=minknow.rpc.manager_pb2.ListDevicesResponse.DeviceLayout(x=3, y=4),
                ports=minknow.rpc.manager_pb2.ListDevicesResponse.RpcPorts(
                    insecure_grpc=9501,
                )
            )
        ]

    def list_devices(self, request, context):
        warnings.warn('Use `flow_cell_positions` instead', DeprecationWarning)

        return minknow.rpc.manager_pb2.ListDevicesResponse(active=self.active)

    def flow_cell_positions(self, request, context) -> iter:
        """
        Provides a snapshot of places where users can insert flow cells.
        """

        # Get random state
        possible_states = minknow.rpc.manager_pb2.FlowCellPosition.State.keys()
        state = random.choice(possible_states)

        flow_cell_positions = [
            minknow.rpc.manager_pb2.FlowCellPosition(
                name='MN0000',
                location=minknow.rpc.manager_pb2.FlowCellPosition.Location(x=8, y=2),
                state=state,
                rpc_ports=minknow.rpc.manager_pb2.FlowCellPosition.RpcPorts(insecure=9501),
            ),
        ]

        total_count = len(flow_cell_positions)

        for flow_cell_position in flow_cell_positions:
            response = minknow.rpc.manager_pb2.FlowCellPositionsResponse(
                total_count=total_count,
                positions=[flow_cell_position],
            )

            yield response
