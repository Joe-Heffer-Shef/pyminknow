import datetime
import logging
import pathlib
import pickle
import time
import uuid
import json
import warnings

from collections import Iterable

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


def to_datetime(timestamp: google.protobuf.timestamp_pb2.Timestamp) -> datetime.datetime:
    try:
        return timestamp.ToDateTime()
    except AttributeError:
        pass


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
        self._start_time = None
        self.end_time = None
        self.device = device
        self._acquisition_run_ids = None

    @property
    def serialisation_dir(self) -> pathlib.Path:
        return self.build_serialisation_dir(device=self.device)

    @property
    def filename(self) -> str:
        return "{name}.{ext}".format(name=self.run_id, ext=self.SERIALISATION_EXT)

    @property
    def as_dict(self) -> dict:
        """Convert to Python data types"""

        return dict(
            state=self.state,
            run_id=self.run_id,
            protocol_id=self.protocol_id,
            _acquisition_run_ids=self._acquisition_run_ids,
            user_info=dict(
                protocol_group_id=self.user_info.protocol_group_id.value,
                sample_id=self.user_info.sample_id.value,
            ),
            args=list(self.args),
            _start_time=self._start_time,
            _end_time=self._end_time,
            device=self.device,
        )

    @property
    def path(self) -> pathlib.Path:
        return self.serialisation_dir.joinpath(self.filename)

    @classmethod
    def build_serialisation_dir(cls, device: dict) -> pathlib.Path:
        return pathlib.Path(pyminknow.config.RUN_DIR).joinpath(device['name'])

    def serialise(self):
        self.serialisation_dir.mkdir(parents=True, exist_ok=True)

        with self.path.open('wb') as file:
            pickle.dump(self.as_dict, file)

            LOGGER.info("Wrote '%s'", file.name)

    def from_dict(self, data: dict):
        self.user_info = self.build_user_info(**data.pop('user_info'))

        for attr, value in data.items():
            setattr(self, attr, value)

    def load(self) -> dict:
        with self.path.open('rb') as file:
            data = pickle.load(file)

            LOGGER.debug("Read '%s'", file.name)

            return data

    def deserialise(self):
        self.from_dict(self.load())

    def build_filenames(self) -> iter:
        """Generate filenames for output data files"""
        templates = {
            'drift_correction_{flow_cell_id}_{acq}.csv',
            'duty_time_{flow_cell_id}_{acq}.csv',
            'final_summary_{flow_cell_id}_{acq}.txt',
            'mux_scan_data_{flow_cell_id}_{acq}.csv',
            'sequencing_summary_{flow_cell_id}_{acq}.txt',
            'throughput_{flow_cell_id}_{acq}.csv',
        }
        for template in templates:
            yield template.format(flow_cell_id=self.flow_cell_id, acq=self.acq_id_short)

        templates = {
            'report_{flow_cell_id}_{day}_{time}_{run_id_short}.md',
            'report_{flow_cell_id}_{day}_{time}_{run_id_short}.pdf',
        }
        for template in templates:
            yield template.format(flow_cell_id=self.flow_cell_id, acq=self.acq_id_short, day=self.day,
                                  time=self.time, run_id_short=self.run_id_short)

    def save_data(self):
        """Write sequence data to disk"""

        # Make subdirectories e.g. "fast5_fail"
        for test in {'fast5', 'fastq'}:
            for result in {'pass', 'fail'}:
                subdir = self.output_path.joinpath("{}_{}".format(test, result))

                # One folder per barcode containing an empty file
                for i in range(25):
                    barcode = "barcode" + str(i).zfill(2)

                    subsubdir = subdir.joinpath(barcode)

                    subsubdir.mkdir(parents=True, exist_ok=True)

                    filename = self.run_code + '_0.' + test
                    subsubdir.joinpath(filename).touch()

        # Create data files
        for filename in self.build_filenames():
            path = self.output_path.joinpath(filename)
            path.touch()

            LOGGER.debug("Wrote '%s'", path)

    @property
    def acq_id_short(self) -> str:
        return self.acquisition_run_id.partition('-')[0]

    @property
    def run_id_short(self) -> str:
        return self.run_id.partition('-')[0]

    @property
    def state(self) -> minknow.rpc.protocol_pb2.ProtocolState:
        return self._state

    @state.setter
    def state(self, state):
        """Change state"""
        self._state = state
        LOGGER.debug('Run %s changed state to %s', self.run_id, self.state)

    def start(self):
        self.start_time = datetime.datetime.utcnow()
        self.state = minknow.rpc.protocol_pb2.ProtocolState.PROTOCOL_RUNNING
        self.serialise()

        LOGGER.debug("Starting run ID: '%s'", self.run_id)
        time.sleep(pyminknow.config.RUN_DURATION)

        self.save_data()
        self.finish()
        self.serialise()

    def finish(self):
        self.end_time = datetime.datetime.utcnow()
        self.state = minknow.rpc.protocol_pb2.ProtocolState.PROTOCOL_COMPLETED

    @property
    def is_complete(self) -> bool:
        return self.state == minknow.rpc.protocol_pb2.ProtocolState.PROTOCOL_COMPLETED

    @property
    def protocol_group_id(self) -> str:
        return self.user_info.protocol_group_id.value

    @property
    def sample_id(self) -> str:
        return self.user_info.sample_id.value

    @property
    def output_path(self) -> pathlib.Path:
        """
        The directory to save the sequencing data
        "/data/protocol_group_id/sample_id/<run code>"
        e.g. "/data/covid19-20200512-1589296413/covid19-20200512-1589296413/20200512_1517_X2_FAN43172_fa3c47d5"
        """
        return pathlib.Path(pyminknow.config.DATA_DIR).joinpath(
            self.protocol_group_id,
            self.sample_id,
            self.run_code,
        )

    @property
    def flow_cell_id(self) -> str:
        return self.device['flow_cell']['flow_cell_id']

    @property
    def run_code(self):
        """
        Generate protocol run identifier "DATE_TIME_DEVICE_FLOWCELLID_PARTOFAQUISITIONID"
        e.g. "20200512_1517_X2_FAN43172_fa3c47d5"
        """
        device_id = self.device['name']
        return "{day}_{time}_{device}_{flow_cell}_{aqu_short}".format(day=self.day, time=self.time, device=device_id,
                                                                      flow_cell=self.flow_cell_id,
                                                                      aqu_short=self.acq_id_short)

    @property
    def day(self) -> str:
        return self._start_time.date().strftime('%Y%m%d')

    @property
    def time(self):
        return self._start_time.strftime('%H%M')

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
    def start_time(self) -> google.protobuf.timestamp_pb2.Timestamp:
        return build_timestamp(self._start_time)

    @start_time.setter
    def start_time(self, value: datetime.datetime):
        self._start_time = value

    @property
    def end_time(self):
        return build_timestamp(self._end_time)

    @end_time.setter
    def end_time(self, value) -> google.protobuf.timestamp_pb2.Timestamp:
        self._end_time = value

    @property
    def info(self) -> minknow.rpc.protocol_pb2.ProtocolRunInfo:
        return minknow.rpc.protocol_pb2.ProtocolRunInfo(
            run_id=self.run_id,
            protocol_id=self.protocol_id,
            args=self.args,
            output_path=str(self.output_path),
            state=self.state,
            start_time=self.start_time,
            end_time=self.end_time,
            user_info=self.user_info,
            acquisition_run_ids=self.acquisition_run_ids,
        )

    @staticmethod
    def build_acquisition_run_ids(n: int = 3):
        return [str(uuid.uuid4()) for _ in range(n)]

    @property
    def acquisition_run_ids(self) -> list:
        if not self._acquisition_run_ids:
            self._acquisition_run_ids = self.build_acquisition_run_ids()
        return self._acquisition_run_ids

    @acquisition_run_ids.setter
    def acquisition_run_ids(self, value):
        self._acquisition_run_ids = value

    @property
    def acquisition_run_id(self) -> str:
        return self.acquisition_run_ids[-1]

    @classmethod
    def get_run_ids(cls, device: dict):
        """Chronological order (by start time ascending)"""
        directory = cls.build_serialisation_dir(device=device)
        paths = pathlib.Path(directory).glob('*.{}'.format(cls.SERIALISATION_EXT))
        yield from (
            # Remove file extension
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
    def tag_value(value) -> minknow.rpc.protocol_pb2.ProtocolInfo.TagValue:
        """
        Translate a value in a Python native data type to a ProtocolInfo.TagValue (protocol buffers data type)

        https://github.com/nanoporetech/minknow_lims_interface/blob/master/minknow/rpc/protocol.proto#L174
        """

        type_map = dict(
            bool_value=bool,
            string_value=str,
            float_value=float,
            int_value=int,
            array_value=Iterable,
        )

        for arg, data_type in type_map.items():
            if isinstance(value, data_type):

                # Serialise arrays to JSON format
                if arg == 'array_value':
                    value = json.dumps(list(value))

                kwargs = {arg: value}

                return minknow.rpc.protocol_pb2.ProtocolInfo.TagValue(**kwargs)

        raise ValueError(value)

    @staticmethod
    def get_protocol_info() -> list:
        """Build collection of ProtocolInfo objects"""
        return [
            minknow.rpc.protocol_pb2.ProtocolInfo(
                identifier=protocol['identifier'],
                name=protocol['name'],
                tags={key: ProtocolService.tag_value(value) for key, value in protocol['tags'].items()},
                tag_extraction_result=minknow.rpc.protocol_pb2.ProtocolInfo.TagExtractionResult(
                    success=True,
                    error_report='',
                ),
            ) for protocol in pyminknow.config.PROTOCOLS
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

    def get_run_info(self, request, context) -> minknow.rpc.protocol_pb2.ProtocolRunInfo:
        run_id = request.run_id

        # If no run ID is provided, information about the most recently started protocol run is provided
        run = Run(run_id=run_id or self.latest_run_id, device=self.device)
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
