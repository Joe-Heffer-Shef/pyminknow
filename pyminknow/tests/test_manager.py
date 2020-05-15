import unittest

import pyminknow.client
import pyminknow.config


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

        n_positions = 0
        total_count = None
        for response in self.client.flow_cell_positions():
            total_count = response.total_count

            for position in response.positions:
                d = devices[position.name]

                self.assertEqual(position.rpc_ports.insecure, d['ports']['insecure'])

                n_positions += 1

        self.assertEqual(n_positions, total_count)
        self.assertEqual(n_positions, len(devices))


if __name__ == '__main__':
    unittest.main()
