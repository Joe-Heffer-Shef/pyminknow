import unittest

import pyminknow.config

import pyminknow.client

PORT = 8012


class TestProtocolService(unittest.TestCase):
    """Test protocol service"""

    def setUp(self) -> None:
        """Initialise server"""

        self.channel = pyminknow.client.connect(port=PORT)
        self.client = pyminknow.client.DeviceClient(self.channel)

    def test_get_device_info(self):
        self.client.get_device_info()

    def test_get_flow_cell_info(self):
        self.client.get_flow_cell_info()

    def test_get_device_state(self):
        self.client.get_device_state()
