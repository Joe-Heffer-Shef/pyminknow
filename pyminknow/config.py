import os
import pathlib

# Server settings
DEFAULT_HOST = 'localhost'
DEFAULT_PORT = os.getenv('GRPC_INSECURE_PORT', 9501)
GRACE = 1  # seconds

# Data directories
DATA_DIR = os.environ.get('MINKNOW_DATA_DIR', '/data')
RUN_DIR = pathlib.Path.home().joinpath('runs')

# Sequencer info
PRODUCT_CODE = 'GRD-X5B002'
DESCRIPTION = 'GridION X5 (Mock)'
SERIAL = 'GXB01484-MOCK'
NETWORK_NAME = 'GXB01484-MOCK'
PROTOCOLS = (
    dict(
        identifier='sequencing/sequencing_MIN106_MIN107_RNA:FLO-MIN106:SQK-RNA002:True',
        name='sequencing/sequencing_MIN106_MIN107_RNA',
        tags={
            'experiment type': 'sequencing',
            'flow cell': 'FLO-MIN106',
            'kit': 'SQK-RNA002',
            'kit_category': ['RNA', 'PCR-Free', 'No Multiplexing'],
            'barcoding': False,
        },
    ),
    dict(
        identifier='sequencing/sequencing_MIN106_MIN107_RNA:FLO-MIN107:SQK-RNA002:True',
        name='sequencing/sequencing_MIN106_MIN107_RNA',
        tags={
            'experiment type': 'sequencing',
            'flow cell': 'FLO-MIN107',
            'kit': 'SQK-RNA002',
            'kit_category': ['RNA', 'PCR-Free', 'No Multiplexing'],
            'barcoding': False,
        },
    ),
    dict(
        identifier='sequencing/sequencing_MIN106_DNA:FLO-MIN106:SQK-LSK109:True',
        name='sequencing/sequencing_MIN106_DNA',
        tags={
            'experiment type': 'sequencing',
            'flow cell': 'FLO-MIN106',
            'kit': 'SQK-LSK109',
            'kit_category': ['DNA', 'RNA', 'PCR', 'PCR-Free', 'No Multiplexing', 'Multiplexing'],
            'barcoding': False,
        },
    ),
)
DEVICES = (
    dict(name='X1', layout=dict(x=0, y=0), ports=dict(secure=8013, insecure=8012),
         flow_cell=dict(flow_cell_id='FAN43224')),
    dict(name='X2', layout=dict(x=1, y=0), ports=dict(secure=8005, insecure=8004),
         flow_cell=dict(flow_cell_id='FAN43512')),
    dict(name='X3', layout=dict(x=2, y=0), ports=dict(secure=8009, insecure=8008),
         flow_cell=dict(flow_cell_id='FAN43512')),
    dict(name='X4', layout=dict(x=3, y=0), ports=dict(secure=8017, insecure=8016), flow_cell=None),
    dict(name='X5', layout=dict(x=4, y=0), ports=dict(secure=8001, insecure=8000), flow_cell=None),
)

RUN_DURATION = 1  # seconds
