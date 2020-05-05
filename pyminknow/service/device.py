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

    def __init__(self, *args, device: dict, **kwargs):
        super().__init__(*args, **kwargs)
        self.device = device

    def get_device_state(self, request, context):
        # Pick a random state
        possible_states = minknow.rpc.device_pb2.GetDeviceStateResponse.DeviceState.keys()
        device_state = random.choice(possible_states)

        return minknow.rpc.device_pb2.GetDeviceStateResponse(device_state=device_state)

    @property
    def flow_cell(self):
        return self.device['flow_cell']

    def get_flow_cell_info(self, request, context):
        return minknow.rpc.device_pb2.GetFlowCellInfoResponse(
            has_flow_cell=True,
            flow_cell_id=self.flow_cell['flow_cell_id'],
            channel_count=512,
            wells_per_channel=4,
            asic_id=5287869,
            product_code="FLO-MIN106",
            temperature_offset=327.6700134277344,
            asic_version="IA02D",
            asic_id_str="5287869",
        )

    def get_device_info(self, request, context):
        # https://github.com/nanoporetech/minknow_lims_interface/blob/master/minknow/rpc/device.proto#L109
        return minknow.rpc.device_pb2.GetDeviceInfoResponse(
            device_id='X1',
            device_type=2,  # GRIDION
            is_simulated=True,
            max_channel_count=512,
            max_wells_per_channel=4,
            can_set_temperature=True,
            digitisation=8192,
            location_defined=True,
            firmware_version=[minknow.rpc.device_pb2.GetDeviceInfoResponse.ComponentVersion(
                component='GridION FPGA',
                version='1.1.3',
            )],
        )
