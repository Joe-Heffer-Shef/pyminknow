import logging
import unittest

import google.protobuf.internal.containers
import minknow_api.tools.protocols
import minknow_api.protocol_pb2

import pyminknow.config

# Use the first device
PORT = pyminknow.config.DEVICES[0]['ports']['insecure']


class TestProtocolService(unittest.TestCase):
    """Test protocol service"""

    def setUp(self) -> None:
        """Initialise server"""

        logging.basicConfig(level=logging.WARNING)

    @unittest.skip
    def test_start_protocol(self):
        # TODO
        pass
        # minknow_api.tools.protocols.start_protocol()
        # response = self.client.start_protocol(
        #     identifier='sequencing/sequencing_MIN106_DNA:FLO-MIN106:SQK-LSK109:True',
        #     user_info=dict(
        #         protocol_group_id='covid19-20200512-1589297081',
        #         sample_id='covid19-20200512-1589297081',
        #     ),
        #     args=[
        #         "--fast5=on",
        #         "--fast5_data", "trace_table", "fastq", "raw", "zlib_compress",
        #         "--base_calling=on",
        #         "--fastq=on",
        #         "--barcoding_kits", "EXP-NBD114", "EXP-NBD104",
        #         "--experiment_time=24"
        #     ],
        # )
        #
        # self.assertIsInstance(response, minknow_api.protocol_pb2.StartProtocolResponse)
        # run_id = response.run_id
        #
        # self.assertIsInstance(run_id, str)
        #
        # return run_id

    @unittest.skip
    def test_get_run_info(self):
        run_id = self.test_start_protocol()

        protocol_run_info = self.client.get_run_info(run_id)

        self.assertIsInstance(protocol_run_info, minknow_api.protocol_pb2.ProtocolRunInfo)

        self.assertEqual(run_id, protocol_run_info.run_id)

    @unittest.skip
    def test_list_protocols(self):
        response = self.client.list_protocols()
        self.assertIsInstance(response, minknow_api.protocol_pb2.ListProtocolsResponse)

        for protocol in response.protocols:
            self.assertIsNotNone(protocol.identifier)
            self.assertIsInstance(protocol.identifier, str)

    @unittest.skip
    def test_list_protocol_runs(self):
        response = self.client.list_protocol_runs()
        self.assertIsInstance(response, minknow_api.protocol_pb2.ListProtocolRunsResponse)
        self.assertIsInstance(response.run_ids, google.protobuf.internal.containers.RepeatedScalarFieldContainer)

        for run_id in response.run_ids:
            self.assertIsInstance(run_id, str)


if __name__ == '__main__':
    unittest.main()
