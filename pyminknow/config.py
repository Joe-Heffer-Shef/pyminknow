import os
import pathlib

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 9501
GRACE = 5  # seconds

PROTOCOLS = (
    'PROTOCOL_A',
    'PROTOCOL_B',
    'PROTOCOL_C',
)

DATA_DIR = os.environ['MINKNOW_DATA_DIR']
RUN_DIR = pathlib.Path.home().joinpath('runs')

PRODUCT_CODE = 'MIN-101B-FAKE'
DESCRIPTION = 'Fake MinIT'
SERIAL = 'FAKE-0123456789'
FLOW_CELL_ID = 'FLO-MIN000'
