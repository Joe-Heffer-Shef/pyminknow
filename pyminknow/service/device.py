import logging

import service.mixins
import minknow.rpc.device_pb2
import minknow.rpc.device_pb2_grpc

LOGGER = logging.getLogger(__name__)


class DeviceService(minknow.rpc.device_pb2_grpc.DeviceServiceServicer, service.mixins.ServiceMixin):
    """
    Device service
    """
    server_adder = minknow.rpc.device_pb2_grpc.add_DeviceServiceServicer_to_server

    possible_states = {'DEVICE_READY', 'DEVICE_DISCONNECTED'}

    def get_device_state(self, request, context):
        # Pick a random state
        device_state = self.possible_states.pop()

        return minknow.rpc.device_pb2.GetDeviceStateResponse(device_state=device_state)
