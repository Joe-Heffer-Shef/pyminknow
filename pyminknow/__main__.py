import argparse
import logging

import pyminknow.config as config
import pyminknow.server

LOGGER = logging.getLogger(__name__)

DESCRIPTION = """
This service mimics a Nanopore minKNOW gene sequencing device by using its gRPC interface.
"""

USAGE = """
python pyminknow --help
"""


def get_args():
    """Command-line arguments"""
    parser = argparse.ArgumentParser(usage=USAGE, description=DESCRIPTION)

    parser.add_argument('-v', '--verbose', action='store_true', help='Debug logging')
    parser.add_argument('-p', '--port', type=int, default=config.DEFAULT_PORT, help='Listen on this port')
    parser.add_argument('-g', '--grace', type=int, default=config.GRACE, help='Grace period (seconds) when stopping')

    return parser.parse_args()


def configure_logging(verbose: bool = False):
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)
    logging.captureWarnings(capture=True)


def main():
    args = get_args()
    configure_logging(verbose=args.verbose)

    server = pyminknow.server.Server(device_port=args.port)
    server.serve(grace=args.grace)


if __name__ == '__main__':
    main()
