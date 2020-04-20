import logging
import random

import minknow.rpc.device_pb2
import minknow.rpc.device_pb2_grpc

LOGGER = logging.getLogger(__name__)


class DeviceService(minknow.rpc.device_pb2_grpc.DeviceServiceServicer):
    """
    Device service
    """
    add_to_server = minknow.rpc.device_pb2_grpc.add_DeviceServiceServicer_to_server

    def get_device_state(self, request, context):
        # Pick a random state
        possible_states = minknow.rpc.device_pb2.GetDeviceStateResponse.DeviceState.keys()
        device_state = random.choice(possible_states)

        return minknow.rpc.device_pb2.GetDeviceStateResponse(device_state=device_state)

    def get_flow_cell_info(self, request, context):
        return minknow.rpc.device_pb2.GetFlowCellInfoResponse(
            has_flow_cell=True,
            flow_cell_id="FAH00000",
        )
