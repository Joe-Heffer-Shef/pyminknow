import logging
import uuid
import random
import datetime

import minknow.rpc.protocol_pb2
import minknow.rpc.protocol_pb2_grpc

import config

LOGGER = logging.getLogger(__name__)


class ProtocolService(minknow.rpc.protocol_pb2_grpc.ProtocolServiceServicer):
    """
    Protocol service
    """
    add_to_server = minknow.rpc.protocol_pb2_grpc.add_ProtocolServiceServicer_to_server

    runs = dict()

    def list_protocols(self, request, context):
        if request.force_reload:
            self.clear_protocol_cache()

        protocols = self.build_protocols()

        return minknow.rpc.protocol_pb2.ListProtocolsResponse(protocols=protocols)

    def clear_protocol_cache(self):
        raise NotImplementedError

    @staticmethod
    def build_protocols() -> list:
        return [
            minknow.rpc.protocol_pb2.ProtocolInfo(
                identifier=protocol_name,
                name=protocol_name,
            ) for protocol_name in config.PROTOCOLS
        ]

    def get_run_info(self, request, context):
        return minknow.rpc.protocol_pb2.ProtocolRunInfo(
            run_id=request.run_id,
        )

    @classmethod
    def make_run_id(cls) -> str:
        return uuid.uuid4().hex

    @classmethod
    def _start_protocol(cls, identifier, *args):
        """Emulate a real process running"""
        LOGGER.info("Starting protocol %s (Args: %s)", identifier, args)

        run_id = cls.make_run_id()

        LOGGER.info("Starting run ID: %s", run_id)

        cls.runs[run_id] = dict(
            protocol_id=identifier,
            args=args,
            output_path='/path/to/output',
            # Pick a random state
            state=random.choice(minknow.rpc.protocol_pb2.ProtocolState.keys()),
            start_time=datetime.datetime.utcnow(),
            end_time=None,
        )

        return run_id

    def start_protocol(self, request, context):
        LOGGER.info(request.user_info)
        LOGGER.info("Protocol group ID: %s", request.user_info.protocol_group_id)
        LOGGER.info("Sample ID: %s", request.user_info.sample_id)

        run_id = self._start_protocol(identifier=request.identifier, *request.args)

        return minknow.rpc.protocol_pb2.StartProtocolResponse(run_id=run_id)

    def get_run_info(self, request, context):
        run_id = request.run_id

        # If no run ID is provided, information about the most recently started protocol run is provided
        if not run_id:
            raise NotImplementedError

        run_info = self.runs[run_id]

        return minknow.rpc.protocol_pb2.ProtocolRunInfo(**run_info)
