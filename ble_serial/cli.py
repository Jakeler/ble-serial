from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, Namespace
from ble_serial import DEFAULT_PORT, DEFAULT_PORT_MSG

def parse_args() -> Namespace:
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter, 
        description='Create virtual serial ports from BLE devices.')

    parser.add_argument('-v', '--verbose', dest='verbose', action='count', default=0,
        help='Increase verbosity, can be specified multiple times for connection/DBus debugging')

    con_group = parser.add_argument_group('connection parameters')
    con_group.add_argument('-t', '--timeout', dest='timeout', required=False, default=5.0, type=float, metavar='SEC',
        help='BLE connect/discover timeout in seconds')
    con_group.add_argument('-i', '--interface', dest='adapter', required=False, default='hci0',
        help='BLE host adapter number to use')
    con_group.add_argument('-m', '--mtu', dest='mtu', required=False, default=20, type=int,
        help='Max. bluetooth packet data size in bytes used for sending')

    dev_group = parser.add_argument_group('device parameters')
    dev_group.add_argument('-g', '--role', dest='gap_role', required=False, default='client', choices=['server', 'client'],
        help='Operate as BLE role: client (BLE central), server (BLE peripheral)')
    dev_group.add_argument('-n', '--name', dest='gap_name', required=False,
        help='Custom display name in BLE server mode, uses "BLE Serial Server {PID}" otherwise. Prefix for logs lines in all modes.')
    dev_group.add_argument('-d', '--dev', dest='device', required=False,
        help='BLE device address to connect (hex format, can be separated by colons)')
    dev_group.add_argument('-a', '--address-type', dest='addr_type', required=False, choices=['public', 'random'], default='public',
        help='BLE address type, only relevant on Windows, ignored otherwise')
    dev_group.add_argument('-s', '--service-uuid', dest='service_uuid', required=False,
        help='''In "client" mode - service UUID used for scanning of potential devices.
        In "server" mode - service UUID used to provide read/write GATT characteristics. ''')
    dev_group.add_argument('-r', '--read-uuid', dest='read_uuid', required=False,
        help='''The GATT characteristic to subscribe to notifications to read the serial data. 
        If omitted, will be auto generated based on service UUID''')
    dev_group.add_argument('-w', '--write-uuid', dest='write_uuid', required=False,
        help='''The GATT characteristic to write the serial data, you might use "ble-scan -d" to find it out.
        If omitted, will be auto generated based on service UUID''')
    dev_group.add_argument('--permit', dest='mode', required=False, default='rw', choices=['ro', 'rw', 'wo'],
        help='Restrict transfer direction on bluetooth: read only (ro), read+write (rw), write only (wo)')
    dev_group.add_argument('--write-with-response', dest='write_with_response', required=False, action='store_true',
        help='Wait for a response from the remote device before sending more. Better data integrity, higher latency and less throughput')


    log_group = parser.add_argument_group('logging options')
    log_group.add_argument('-l', '--log', dest='filename', required=False,
        help='Enable optional logging of all bluetooth traffic to file')
    log_group.add_argument('-b', '--binary', dest='binlog', required=False, action='store_true',
        help='Log data as raw binary, disable transformation to hex. Works only in combination with -l')

    uart_group = parser.add_argument_group('serial port parameters')
    uart_group.add_argument('-p', '--port', dest='port', required=False, default=DEFAULT_PORT,
        help=DEFAULT_PORT_MSG)

    net_group = parser.add_argument_group('network options')
    net_group.add_argument('--expose-tcp-host', dest='tcp_host', required=False, default='127.0.0.1',
        help='Network interface for the server listen on')
    net_group.add_argument('--expose-tcp-port', dest='tcp_port', required=False, default=None, type=int,
        help='Port to listen on, disables local serial port and enables TCP server if specified')

    args = parser.parse_args()

    client_checks(parser, args)
    server_checks(parser, args)

    return args


def client_checks(parser: ArgumentParser, args: Namespace):
    if args.gap_role != 'client':
        return # not applicable
    if not args.device and not args.service_uuid:
        parser.error('at least one of -d/--dev and -s/--service-uuid required')

def server_checks(parser: ArgumentParser, args: Namespace):
    if args.gap_role != 'server':
        return # not applicable
    if not args.service_uuid:
        parser.error('Server role requires -s/--service-uuid')

