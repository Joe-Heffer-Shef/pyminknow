import logging
import uuid
import datetime
import warnings
import os.path

from collections import OrderedDict

import google.protobuf.wrappers_pb2
import google.protobuf.timestamp_pb2

import minknow.rpc.protocol_pb2
import minknow.rpc.protocol_pb2_grpc

import pyminknow.config

LOGGER = logging.getLogger(__name__)


def build_timestamp(timestamp=None) -> google.protobuf.timestamp_pb2.Timestamp:
    """Convert Python datetime to Protobuf Timestamp"""
    # https://github.com/protocolbuffers/protobuf/issues/3986
    proto_timestamp = google.protobuf.timestamp_pb2.Timestamp()
    return proto_timestamp.FromDatetime(timestamp or datetime.datetime.utcnow())


class Run:

    def __init__(self, protocol_id: str, user_info: minknow.rpc.protocol_pb2.ProtocolRunUserInfo, args: list):
        self.state = None
        self.run_id = self.make_run_id()
        self.protocol_id = protocol_id
        self.user_info = user_info
        self.args = args
        self.start_time = datetime.datetime.utcnow()
        self.end_time = None

        LOGGER.debug("Starting run ID: %s", self.run_id)
        LOGGER.debug("Protocol group ID: %s", user_info.protocol_group_id.value)
        LOGGER.debug("Sample ID: %s", user_info.sample_id.value)

        self.start()

    def serialise_data(self):
        os.makedirs(self.output_path)

        # Generate some dummy data
        path = os.path.join(self.output_path, 'my_data.txt')
        with open(path, 'w') as file:
            file.write('Hello world!\n')

    def start(self):
        self.state = minknow.rpc.protocol_pb2.ProtocolState.PROTOCOL_RUNNING

        self.serialise_data()

        self.finish()

    def finish(self):
        self.state = minknow.rpc.protocol_pb2.ProtocolState.PROTOCOL_RUNNING
        self.end_time = datetime.datetime.utcnow()

    @property
    def output_path(self):
        return os.path.join(pyminknow.config.DATA_DIR, self.run_id)

    @classmethod
    def make_run_id(cls) -> str:
        """Generate random new run identifier"""
        return uuid.uuid4().hex

    @classmethod
    def build_user_info(cls, protocol_group_id: str, sample_id: str):
        return minknow.rpc.protocol_pb2.ProtocolRunUserInfo(
            protocol_group_id=google.protobuf.wrappers_pb2.StringValue(value=protocol_group_id),
            sample_id=google.protobuf.wrappers_pb2.StringValue(value=sample_id),
        )

    @property
    def start_time(self):
        return build_timestamp(self._start_time)

    @start_time.setter
    def start_time(self, value):
        self._start_time = value

    @property
    def end_time(self):
        return build_timestamp(self._end_time)

    @end_time.setter
    def end_time(self, value):
        self._end_time = value

    @property
    def run_info(self):
        return minknow.rpc.protocol_pb2.ProtocolRunInfo(
            protocol_id=self.protocol_id,
            args=self.args,
            output_path=self.output_path,
            state=self.state,
            start_time=self.start_time,
            end_time=self.end_time,
            user_info=self.user_info,
        )


class ProtocolService(minknow.rpc.protocol_pb2_grpc.ProtocolServiceServicer):
    """
    Protocol service
    """
    add_to_server = minknow.rpc.protocol_pb2_grpc.add_ProtocolServiceServicer_to_server
    runs = OrderedDict()

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
            ) for protocol_name in pyminknow.config.PROTOCOLS
        ]

    @classmethod
    def _start_protocol(cls, identifier, user_info, args):
        """Emulate a real process running"""
        LOGGER.info("Starting protocol %s (Args: %s)", identifier, args)

        run = Run(protocol_id=identifier, user_info=user_info, args=args)
        cls.runs[run.run_id] = run

        return run.run_id

    def start_protocol(self, request, context):

        run_id = self._start_protocol(identifier=request.identifier, user_info=request.user_info, args=request.args)

        return minknow.rpc.protocol_pb2.StartProtocolResponse(run_id=run_id)

    @property
    def latest_run_id(self):
        """The identifier of the most recently-started run"""
        return next(reversed(self.runs.keys()))

    @property
    def run_ids(self) -> list:
        """Chronological order (by start time ascending)"""
        return list(self.runs.keys())

    def get_run_info(self, request, context):
        run_id = request.run_id

        # If no run ID is provided, information about the most recently started protocol run is provided
        if not run_id:
            run_id = self.latest_run_id

        run = self.runs[run_id]

        return run.run_info

    def set_sample_id(self, request, context):
        """
        Specify the sample identifier to set for the next protocol (deprecated)
        """

        warnings.warn('The sample_id should be set in the request when a protocol starts', DeprecationWarning)

        LOGGER.debug('Sample ID: %s', request.sample_id)

        return minknow.rpc.protocol_pb2.SetSampleIdResponse()

    def list_protocol_runs(self, request, context):
        """List previously started protocol run ids (including any current protocol), in order of starting."""
        return minknow.rpc.protocol_pb2.ListProtocolRunsResponse(run_ids=self.run_ids)
