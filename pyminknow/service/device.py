"""
Device service definitions
"""

import logging

import minknow.rpc.device_pb2
import minknow.rpc.device_pb2_grpc

LOGGER = logging.getLogger(__name__)


class DeviceService(minknow.rpc.device_pb2_grpc.DeviceServiceServicer):
    """
    Device service
    """

    def map_to_server(self, server):
        minknow.rpc.device_pb2_grpc.add_DeviceServiceServicer_to_server(self, server)

    def get_device_state(self, request, context):
        """Get information about the current device state.

        Information in this call may change as the device is used with MinKNOW, for example,
        by unplugging or plugging in the device.
        Since 1.12
        """

        device_state = minknow.rpc.device_pb2.GetDeviceStateResponse.DeviceState.DEVICE_READY

        return minknow.rpc.device_pb2.GetDeviceStateResponse(device_state=device_state)
