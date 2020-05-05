import datetime
import logging
import os.path
import pathlib
import pickle
import time
import uuid
import warnings

import google.protobuf.timestamp_pb2
import google.protobuf.wrappers_pb2

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

    def __init__(self, run_id: str = None, protocol_id: str = None, user_info=None, args: list = None,
                 device: dict = None):
        self.run_id = run_id or self.make_run_id()
        self._state = None
        self.protocol_id = protocol_id
        self.user_info = user_info
        self.args = list(args or ())
        self.start_time = datetime.datetime.utcnow()
        self.end_time = None
        self.device = device

    @property
    def serialisation_dir(self) -> str:
        return self.build_serialisation_dir(device=self.device)

    @property
    def filename(self) -> str:
        return "{name}.{ext}".format(name=self.run_id, ext=self.SERIALISATION_EXT)

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
            device=self.device,
        )

    @property
    def path(self) -> str:
        return os.path.join(self.serialisation_dir, self.filename)

    @classmethod
    def build_serialisation_dir(cls, device: dict) -> str:
        return os.path.join(pyminknow.config.RUN_DIR, device['name'])

    def serialise(self):
        os.makedirs(self.serialisation_dir, exist_ok=True)

        with open(self.path, 'wb') as file:
            pickle.dump(self.as_dict, file)

            LOGGER.info("Wrote '%s'", file.name)

    def from_dict(self, data: dict):
        self.user_info = self.build_user_info(**data.pop('user_info'))

        for attr, value in data.items():
            setattr(self, attr, value)

    def load(self) -> dict:
        with open(self.path, 'rb') as file:
            data = pickle.load(file)

            LOGGER.debug("Read '%s'", file.name)

            return data

    def deserialise(self):
        self.from_dict(self.load())

    def save_data(self):
        """Write sequence data to disk"""

        filename = 'my_data.txt'
        path = os.path.join(self.output_directory, filename)

        # Write to disk
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
        LOGGER.debug('Run %s changed state to %s', self.run_id, self.state)
        self.serialise()

    def start(self):
        self.state = minknow.rpc.protocol_pb2.ProtocolState.PROTOCOL_RUNNING

        LOGGER.debug("Starting run ID: %s", self.run_id)
        LOGGER.debug("Protocol group ID: %s", self.user_info.protocol_group_id.value)
        LOGGER.debug("Sample ID: %s", self.user_info.sample_id.value)

        self.save_data()
        self.finish()

    def finish(self):
        self.end_time = datetime.datetime.utcnow()
        self.state = minknow.rpc.protocol_pb2.ProtocolState.PROTOCOL_COMPLETED

    @property
    def is_complete(self) -> bool:
        return self.state == minknow.rpc.protocol_pb2.ProtocolState.PROTOCOL_COMPLETED

    @property
    def output_directory(self) -> str:
        """
        The directory to save the sequencing data
        e.g. "/data/external_run_id/external_run_id/protcol_run_id"
        """
        external_run_id = str(self.user_info.protocol_group_id)
        return os.path.join(
            pyminknow.config.DATA_DIR,
            external_run_id,
            external_run_id,
            self.run_id,
        )

    @property
    def data_subdir(self):
        """
        Generate protocol run identifier
        e.g. "DATE_TIME_DEVICE_FLOWCELLID_PARTOFAQUISITIONID"
        """
        device_id = self.device['name']
        flow_cell_id = self.device['flow_cell']['flow_cell_id']
        day = self.start_time.date().strftime('%Y%m%d')
        clock_time = self.start_time.strftime('%H%M')
        unique = self.run_id.partition('-')[0]
        return "{day}_{time}_{device}_{flow_cell}_{acq}".format(day=day, time=clock_time, device=device_id,
                                                                flow_cell=flow_cell_id, acq=unique)

    @classmethod
    def make_run_id(cls) -> str:
        return str(uuid.uuid4())

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
    def info(self) -> minknow.rpc.protocol_pb2.ProtocolRunInfo:
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
    def get_run_ids(cls, device: dict):
        """Chronological order (by start time ascending)"""
        directory = cls.build_serialisation_dir(device=device)
        paths = pathlib.Path(directory).glob('*.{}'.format(cls.SERIALISATION_EXT))
        yield from (
            # remove file ext
            _path.stem for _path in
            # Sort by creation time
            sorted(paths, key=lambda _path: _path.stat().st_ctime)
        )

    @classmethod
    def latest_run_id(cls, device: dict) -> str:
        return next(cls.get_run_ids(device))


class ProtocolService(minknow.rpc.protocol_pb2_grpc.ProtocolServiceServicer):
    """
    Protocol service

    https://github.com/nanoporetech/minknow_lims_interface/blob/master/minknow/rpc/protocol.proto
    """
    add_to_server = minknow.rpc.protocol_pb2_grpc.add_ProtocolServiceServicer_to_server

    def __init__(self, *args, device: dict, **kwargs):
        super().__init__(*args, **kwargs)
        self.device = device
        self.sample_id = None

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

    def _start_protocol(self, identifier, user_info, args):
        """Emulate a real process running"""
        LOGGER.info("Starting protocol %s (Args: %s)", identifier, args)

        run = Run(protocol_id=identifier, user_info=user_info, args=args, device=self.device.copy())
        run.start()

        return run.run_id

    def start_protocol(self, request, context):

        run_id = self._start_protocol(identifier=request.identifier, user_info=request.user_info, args=request.args)

        return minknow.rpc.protocol_pb2.StartProtocolResponse(run_id=run_id)

    @property
    def latest_run_id(self):
        """The identifier of the most recently-started run"""
        return Run.latest_run_id(device=self.device)

    @property
    def run_ids(self) -> list:
        return list(Run.get_run_ids(device=self.device))

    def get_run_info(self, request, context):
        run_id = request.run_id

        # If no run ID is provided, information about the most recently started protocol run is provided
        if not run_id:
            run_id = self.latest_run_id

        run = Run(run_id=run_id, device=self.device)
        run.deserialise()

        return run.info

    def set_sample_id(self, request, context):
        """
        Specify the sample identifier to set for the next protocol (deprecated)
        """

        warnings.warn('The sample_id should be set in the request when a protocol starts', DeprecationWarning)

        self.sample_id = request.sample_id

        LOGGER.debug('Sample ID: %s', self.sample_id)

        return minknow.rpc.protocol_pb2.SetSampleIdResponse()

    def list_protocol_runs(self, request, context):
        """List previously started protocol run ids (including any current protocol), in order of starting."""
        return minknow.rpc.protocol_pb2.ListProtocolRunsResponse(run_ids=self.run_ids)

    def wait_for_finished(self, request, context) -> minknow.rpc.protocol_pb2.ProtocolRunInfo:

        run = Run(run_id=request.run_id, device=self.device)
        run.deserialise()

        while True:

            if run.is_complete:
                return run.info

            time.sleep(1)
