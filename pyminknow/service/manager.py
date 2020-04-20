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

    def list_devices(self, request, context):
        warnings.warn('Use `flow_cell_positions` instead', DeprecationWarning)

        active = [
            minknow.rpc.manager_pb2.ListDevicesResponse.ActiveDevice(
                name='MN0004',
                layout=minknow.rpc.manager_pb2.ListDevicesResponse.DeviceLayout(x=3, y=4),
                ports=minknow.rpc.manager_pb2.ListDevicesResponse.RpcPorts(
                    secure=12411,
                    insecure_grpc=24115,
                    insecure_web=23432,
                )
            )
        ]

        LOGGER.debug("Listing %s active devices", len(active))

        return minknow.rpc.manager_pb2.ListDevicesResponse(
            inactive=['MN0001', 'MN0002'],
            pending=['MN0003'],
            active=active,
        )

    def flow_cell_positions(self, request, context) -> iter:
        """
        Provides a snapshot of places where users can insert flow cells.
        """

        # Get random state
        possible_states = minknow.rpc.manager_pb2.FlowCellPosition.State.keys()
        state = random.choice(possible_states)

        flow_cell_positions = [
            minknow.rpc.manager_pb2.FlowCellPosition(
                name='TEST000123',
                location=minknow.rpc.manager_pb2.FlowCellPosition.Location(x=8, y=2),
                state=state,
                rpc_ports=minknow.rpc.manager_pb2.FlowCellPosition.RpcPorts(
                    secure=123,
                    insecure=456,
                    secure_grpc_web=543,
                    insecure_grpc_web=4523,
                ),
                error_info='',
            ),
        ]

        total_count = len(flow_cell_positions)

        for flow_cell_position in flow_cell_positions:
            response = minknow.rpc.manager_pb2.FlowCellPositionsResponse(
                total_count=total_count,
                positions=[flow_cell_position],
            )

            yield response
