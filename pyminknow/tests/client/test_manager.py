import unittest

import pyminknow.config

import pyminknow.client


class TestProtocolService(unittest.TestCase):
    """Test protocol service"""

    def setUp(self) -> None:
        """Initialise server"""

        self.channel = pyminknow.client.connect()
        self.client = pyminknow.client.ManagerClient(self.channel)

    def test_describe_host(self):
        host = self.client.describe_host()

        self.assertEqual(host.product_code, pyminknow.config.PRODUCT_CODE)
        self.assertEqual(host.description, pyminknow.config.DESCRIPTION)
        self.assertEqual(host.serial, pyminknow.config.SERIAL)
        self.assertEqual(host.network_name, pyminknow.config.NETWORK_NAME)

    def test_flow_cell_positions(self):
        devices = {d['name']: d for d in pyminknow.config.DEVICES}

        for flow_cell_positions in self.client.flow_cell_positions():
            for flow_cell_position in flow_cell_positions.positions:
                d = devices[flow_cell_position.name]

                self.assertEqual(flow_cell_position.rpc_ports.insecure, d['ports']['insecure'])
