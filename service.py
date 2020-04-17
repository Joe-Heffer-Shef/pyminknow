"""
Service definitions
"""

import minknow.rpc.manager_pb2
import minknow.rpc.manager_pb2_grpc


class Location(minknow.rpc.manager_pb2.FlowCellPosition.Location):
    """
    Flow Cell Position

    x = The column (counting from 0, left-to-right) of the flow cell position
        on the sequencing unit when viewed from above/in front.

    y = The row (counting from 0, top-to-bottom) of the flow cell position on
        the sequencing unit when viewed from above/in front.
    """
    pass


class RpcPorts(minknow.rpc.manager_pb2.FlowCellPosition.RpcPorts):
    pass


class FlowCellPosition(minknow.rpc.manager_pb2.FlowCellPosition):
    """
    Flow Cell Position
    """
    pass


class ManagerServiceServicer(minknow.rpc.manager_pb2_grpc.ManagerServiceServicer):

    def map_to_server(self, server):
        return minknow.rpc.manager_pb2_grpc.add_ManagerServiceServicer_to_server(self, server)

    def flow_cell_positions(self, request, context) -> iter:
        """
        Provides a snapshot of places where users can insert flow cells.

        It has a streamed response in case there are too many positions
        to fit into a single response, but normally there should
        only be a single response.

        ProtoBuf signature:
        rpc flow_cell_positions (FlowCellPositionsRequest) returns (stream FlowCellPositionsResponse) {}
        """

        LOGGER.debug(context)
        LOGGER.debug(request)

        flow_cell_positions = [
            FlowCellPosition(
                name='My test machine',
                location=Location(x=0, y=0),
                state=minknow.rpc.manager_pb2.FlowCellPosition.State.STATE_RUNNING,
                rpc_ports=RpcPorts(
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
