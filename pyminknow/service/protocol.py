import logging
import uuid

import minknow.rpc.protocol_pb2
import minknow.rpc.protocol_pb2_grpc

LOGGER = logging.getLogger(__name__)


class ProtocolService(minknow.rpc.protocol_pb2_grpc.ProtocolServiceServicer):
    """
    Protocol service
    """
    server_adder = minknow.rpc.protocol_pb2_grpc.add_ProtocolServiceServicer_to_server

    @staticmethod
    def make_run_id() -> str:
        return uuid.uuid4().hex

    def get_run_info(self, request, context):
        response = minknow.rpc.protocol_pb2.ProtocolRunInfo(
            run_id=request.run_id,
            protocol_id=None,
        )

        return response

    def _start_protocol(self, identifier, *args):
        LOGGER.info("Starting protocol %s (%s)", identifier, args)

    def start_protocol(self, request, context):
        LOGGER.info(request.user_info)
        LOGGER.info("Group ID: %s", request.user_info.protocol_group_id)
        LOGGER.info("Sample ID: %s", request.user_info.sample_id)

        self._start_protocol(identifier=request.identifier, *request.args)

        run_id = self.make_run_id()

        LOGGER.info("Run ID: %s", run_id)

        response = minknow.rpc.protocol_pb2.StartProtocolResponse(run_id=run_id)

        return response
