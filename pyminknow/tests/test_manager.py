import unittest

import pyminknow.config

import minknow_api.manager


class TestProtocolService(unittest.TestCase):
    """Test protocol service"""

    def setUp(self) -> None:
        """Initialise server"""

        self.client = minknow_api.manager.Manager(use_tls=False)

    def test_describe_host(self):
        host = self.client.describe_host()

        self.assertEqual(host.product_code, pyminknow.config.PRODUCT_CODE)
        self.assertEqual(host.description, pyminknow.config.DESCRIPTION)
        self.assertEqual(host.serial, pyminknow.config.SERIAL)
        self.assertEqual(host.network_name, pyminknow.config.NETWORK_NAME)

    def test_flow_cell_positions(self):
        devices = {d['name']: d for d in pyminknow.config.DEVICES}

        for flow_cell_position in self.client.flow_cell_positions():
            print(dir(flow_cell_position))
            d = devices[flow_cell_position.name]

            self.assertEqual(flow_cell_position.rpc_ports.insecure, d['ports']['insecure'])
