import logging
import uuid
import time
import datetime
import warnings
import os.path
import pickle
import pathlib

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
    """Protocol run (dummy)"""
    SERIALISATION_EXT = 'pkl'

    def __init__(self, protocol_id: str, user_info: minknow.rpc.protocol_pb2.ProtocolRunUserInfo, args: list):
        self._state = None
        self.run_id = self.make_run_id()
        self.protocol_id = protocol_id
        self.user_info = user_info
        self.args = list(args)
        self.start_time = datetime.datetime.utcnow()
        self.end_time = None

        LOGGER.debug("Starting run ID: %s", self.run_id)
        LOGGER.debug("Protocol group ID: %s", user_info.protocol_group_id.value)
        LOGGER.debug("Sample ID: %s", user_info.sample_id.value)

    @classmethod
    def build_path(cls, run_id):
        filename = "{name}.{ext}".format(name=run_id, ext=cls.SERIALISATION_EXT)
        return os.path.join(pyminknow.config.RUN_DIR, filename)

    @property
    def as_dict(self) -> dict:
        return dict(
            state=self.state,
            run_id=self.run_id,
            protocol_id=self.protocol_id,
            user_info=dict(
                protocol_group_id=str(self.user_info.protocol_group_id),
                sample_id=str(self.user_info.sample_id),
            ),
            args=self.args,
            start_time=self.start_time,
            end_time=self.end_time,
        )

    @property
    def path(self):
        return self.build_path(self.run_id)

    def serialise(self):
        os.makedirs(pyminknow.config.RUN_DIR, exist_ok=True)

        with open(self.path, 'wb') as file:
            pickle.dump(self.as_dict, file)

            LOGGER.info("Wrote '%s'", file.name)

    @classmethod
    def from_dict(cls, data: dict):
        run = Run(
            protocol_id=data.pop('protocol_id'),
            user_info=cls.build_user_info(**data.pop('user_info')),
            args=data.pop('args'),
        )

        # run.state = minknow.rpc.protocol_pb2.ProtocolState(data.pop('state'))

        for attr, value in data.items():
            setattr(run, attr, value)

        return run

    @classmethod
    def deserialise(cls, run_id: str):
        path = cls.build_path(run_id)
        with open(path, 'rb') as file:
            data = pickle.load(file)

            LOGGER.debug("Read '%s'", file.name)

        run = cls.from_dict(data)

        return run

    def save_data(self):
        """Write sequence data to disk"""

        path = os.path.join(self.output_directory, 'my_data.txt')

        os.makedirs(self.output_directory, exist_ok=True)
        with open(path, 'w') as file:
            # Generate some dummy data
            file.write('Hello world!\n')

            LOGGER.debug("Wrote '%s'", file.name)

    @property
    def state(self) -> minknow.rpc.protocol_pb2.ProtocolState:
        return self._state

    @state.setter
    def state(self, state):
        """Change state"""
        self._state = state
        self.serialise()

    def start(self):
        self.state = minknow.rpc.protocol_pb2.ProtocolState.PROTOCOL_RUNNING
        self.save_data()
        self.finish()

    def finish(self):
        self.end_time = datetime.datetime.utcnow()
        self.state = minknow.rpc.protocol_pb2.ProtocolState.PROTOCOL_COMPLETED

    @property
    def is_complete(self) -> bool:
        return self.state == minknow.rpc.protocol_pb2.ProtocolState.PROTOCOL_COMPLETED

    @property
    def output_directory(self):
        return os.path.join(pyminknow.config.DATA_DIR, self.run_id)

    @classmethod
    def make_run_id(cls) -> str:
        """Generate protocol run identifier"""
        now = datetime.datetime.utcnow()
        day = now.date().strftime('%Y%m%d')
        clock_time = now.strftime('%H%M')
        unique = str(uuid.uuid4()).partition('-')[0]
        return "{}_{}_X1_FAN47535_{}".format(day, clock_time, unique)

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
    def run_info(self) -> minknow.rpc.protocol_pb2.ProtocolRunInfo:
        return minknow.rpc.protocol_pb2.ProtocolRunInfo(
            protocol_id=self.protocol_id,
            args=self.args,
            output_path=self.output_directory,
            state=self.state,
            start_time=self.start_time,
            end_time=self.end_time,
            user_info=self.user_info,
            acquisition_run_ids=self.acquisition_run_ids,
        )

    @property
    def acquisition_run_ids(self) -> list:
        return [str(uuid.uuid4()) for _ in range(3)]

    @classmethod
    def get_run_ids(cls):
        """Chronological order (by start time ascending)"""
        yield from (
            # remove file ext
            _path.stem for _path in
            # Sort by creation time
            sorted(pathlib.Path(pyminknow.config.RUN_DIR).glob('*.{}'.format(cls.SERIALISATION_EXT)),
                   key=lambda _path: _path.stat().st_ctime)
        )

    @classmethod
    def latest_run_id(cls) -> str:
        return next(cls.get_run_ids())


class ProtocolService(minknow.rpc.protocol_pb2_grpc.ProtocolServiceServicer):
    """
    Protocol service

    https://github.com/nanoporetech/minknow_lims_interface/blob/master/minknow/rpc/protocol.proto
    """
    add_to_server = minknow.rpc.protocol_pb2_grpc.add_ProtocolServiceServicer_to_server

    def list_protocols(self, request, context):
        if request.force_reload:
            self.clear_protocol_cache()

        protocols = self.get_protocol_info()

        return minknow.rpc.protocol_pb2.ListProtocolsResponse(protocols=protocols)

    def clear_protocol_cache(self):
        raise NotImplementedError

    @staticmethod
    def get_protocol_info() -> list:
        """Build collection of ProtocolInfo objects"""
        return [
            minknow.rpc.protocol_pb2.ProtocolInfo(
                identifier=protocol_name,
                name=protocol_name,
                tags={
                    'flow cell': minknow.rpc.protocol_pb2.ProtocolInfo.TagValue(string_value="FLO-MIN106"),
                    'kit': minknow.rpc.protocol_pb2.ProtocolInfo.TagValue(string_value="SQK-LSK109"),
                    'experiment type': minknow.rpc.protocol_pb2.ProtocolInfo.TagValue(string_value="sequencing"),
                }
            ) for protocol_name in pyminknow.config.PROTOCOLS
        ]

    @classmethod
    def _start_protocol(cls, identifier, user_info, args):
        """Emulate a real process running"""
        LOGGER.info("Starting protocol %s (Args: %s)", identifier, args)

        run = Run(protocol_id=identifier, user_info=user_info, args=args)
        run.start()

        return run.run_id

    def start_protocol(self, request, context):

        run_id = self._start_protocol(identifier=request.identifier, user_info=request.user_info, args=request.args)

        return minknow.rpc.protocol_pb2.StartProtocolResponse(run_id=run_id)

    @property
    def latest_run_id(self):
        """The identifier of the most recently-started run"""
        return Run.latest_run_id()

    @property
    def run_ids(self) -> list:
        return list(Run.get_run_ids())

    def get_run_info(self, request, context):
        run_id = request.run_id

        # If no run ID is provided, information about the most recently started protocol run is provided
        if not run_id:
            run_id = self.latest_run_id

        run = Run.deserialise(run_id=run_id)

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

    def wait_for_finished(self, request, context) -> minknow.rpc.protocol_pb2.ProtocolRunInfo:

        run = Run.deserialise(request.run_id)

        while True:

            if run.is_complete:
                return run.run_info

            time.sleep(1)
