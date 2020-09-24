import logging
import random

import minknow_api.device_pb2
import minknow_api.device_pb2_grpc

LOGGER = logging.getLogger(__name__)


class DeviceService(minknow_api.device_pb2_grpc.DeviceServiceServicer):
    """
    Device service
    """
    add_to_server = minknow_api.device_pb2_grpc.add_DeviceServiceServicer_to_server

    def __init__(self, *args, device: dict, **kwargs):
        super().__init__(*args, **kwargs)
        self.device = device

    def get_device_state(self, request, context):
        # Pick a random state
        possible_states = minknow_api.device_pb2.GetDeviceStateResponse.DeviceState.keys()
        device_state = random.choice(possible_states)

        return minknow_api.device_pb2.GetDeviceStateResponse(device_state=device_state)

    @property
    def flow_cell(self):
        return self.device.get('flow_cell')

    def get_flow_cell_info(self, request, context):
        if self.flow_cell:
            data = dict(
                has_flow_cell=True,
                flow_cell_id=self.flow_cell['flow_cell_id'],
                channel_count=512,
                wells_per_channel=4,
                product_code="FLO-MIN106",
                user_specified_flow_cell_id="?",
                user_specified_product_code='?',
                temperature_offset=327.6700134277344,
                asic_version="IA02D",
                asic_id_str="5287869",
            )
        else:
            data = dict(has_flow_cell=False)

        return minknow_api.device_pb2.GetFlowCellInfoResponse(**data)

    def get_device_info(self, request, context):
        # https://github.com/nanoporetech/minknow_lims_interface/blob/master/minknow/rpc/device.proto#L109
        return minknow_api.device_pb2.GetDeviceInfoResponse(
            device_id='X1',
            device_type=2,  # GRIDION
            is_simulated=True,
            max_channel_count=512,
            max_wells_per_channel=4,
            can_set_temperature=True,
            digitisation=8192,
            firmware_version=[minknow_api.device_pb2.GetDeviceInfoResponse.ComponentVersion(
                component='GridION FPGA',
                version='1.1.3',
            )],
        )
