"""
Mock minKNOW gRPC client
"""

import argparse
import logging

import grpc

import config
import client.clients

LOGGER = logging.getLogger(__name__)

DESCRIPTION = """
TODO
"""

USAGE = """
TODO
"""


def get_args():
    parser = argparse.ArgumentParser(usage=USAGE, description=DESCRIPTION)

    parser.add_argument('-v', '--verbose', action='store_true', help='Debug logging')
    parser.add_argument('-o', '--host', default=config.DEFAULT_HOST, help='Connect to this host')
    parser.add_argument('-p', '--port', type=int, default=config.DEFAULT_PORT, help='Connect to this port')
    parser.add_argument('-s', '--device_state', action='store_true', help='Get device state')
    parser.add_argument('-l', '--list_protocols', action='store_true', help='List available protocols')
    parser.add_argument('-d', '--list_devices', action='store_true', help='List available devices')
    parser.add_argument('-f', '--flow_cell_positions', action='store_true',
                        help='List all known positions where flow cells can be inserted')

    return parser, parser.parse_args()


def connect(host: str, port: int):
    """
    Connect to the server
    """

    target = '{host}:{port}'.format(host=host, port=port)

    LOGGER.info("Connecting to '%s'...", target)

    channel = grpc.insecure_channel(target=target)

    return channel


def configure_logging(verbose: bool = False):
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)
    logging.captureWarnings(capture=True)


def main():
    parser, args = get_args()
    configure_logging(verbose=args.verbose)

    with connect(host=args.host, port=args.port) as channel:

        # Device state
        if args.device_state:
            client = client.clients.DeviceClient(channel)
            print(client.get_device_state())

        # List protocols
        elif args.list_protocols:
            client = client.clients.ProtocolClient(channel)
            for protocol in client.list_protocols().protocols:
                print(protocol)

        elif args.list_devices or args.flow_cell_positions:
            client = ManagerClient(channel)

            if args.list_devices:
                devices = client.list_devices()
                LOGGER.info("Found %s active devices", len(devices.active))
                for device in devices.active:
                    print(device)

            elif args.flow_cell_positions:
                for item in client.flow_cell_positions():
                    print(item)

            else:
                raise ValueError('Unknown command')

        else:
            parser.print_help()


if __name__ == '__main__':
    main()
