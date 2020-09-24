import unittest

import minknow_api

HOST = 'localhost'
PORT = 8004


class TestDeviceService(unittest.TestCase):
    def setUp(self) -> None:
        self.connection = minknow_api.Connection(host=HOST, port=PORT, use_tls=False)

        self.device = self.connection.device

    # def test_get_device_info(self):
    #     self.device.get_device_info()
    #
    # def test_get_flow_cell_info(self):
    #     self.device.get_flow_cell_info()
