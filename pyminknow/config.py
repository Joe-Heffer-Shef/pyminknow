import os
import pathlib

# Server settings
DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 9501
GRACE = 5  # seconds

# Data directories
DATA_DIR = os.environ.get('MINKNOW_DATA_DIR', '/data')
RUN_DIR = pathlib.Path.home().joinpath('runs')

# Sequencer info
PRODUCT_CODE = 'MIN-101B-FAKE'
DESCRIPTION = 'Fake MinIT'
SERIAL = 'FAKE-0123456789'
FLOW_CELL_ID = 'FLO-MIN000'
PROTOCOLS = (
    'PROTOCOL_A',
    'PROTOCOL_B',
    'PROTOCOL_C',
)
