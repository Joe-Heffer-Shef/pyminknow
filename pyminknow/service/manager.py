import logging

import minknow.rpc.manager_pb2
import minknow.rpc.manager_pb2_grpc

LOGGER = logging.getLogger(__name__)


class ManagerService(minknow.rpc.manager_pb2_grpc.ManagerServiceServicer):
    """
    Manager service
    """
    add_to_server = minknow.rpc.manager_pb2_grpc.add_ManagerServiceServicer_to_server

    def list_devices(self, request, context):
        return minknow.rpc.manager_pb2.ListDevicesResponse(
            inactive=['MN0001', 'MN0002'],
            pending=['MN0003'],
            active=[
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
        )

    def flow_cell_positions(self, request, context) -> iter:
        """
        Provides a snapshot of places where users can insert flow cells.
        """

        LOGGER.debug(context)
        LOGGER.debug(request)

        flow_cell_positions = [
            minknow.rpc.manager_pb2.FlowCellPosition(
                name='My test machine',
                location=minknow.rpc.manager_pb2.FlowCellPosition.Location(x=0, y=0),
                state=minknow.rpc.manager_pb2.FlowCellPosition.State.STATE_RUNNING,
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
                positions=flow_cell_position,
            )

            yield response
