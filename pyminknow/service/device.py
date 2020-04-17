"""
Device service definitions
"""

import logging
import random

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
        possible_states = ('DEVICE_READY', 'DEVICE_DISCONNECTED')
        device_state = random.choice(possible_states)
        return minknow.rpc.device_pb2.GetDeviceStateResponse(device_state=device_state)
