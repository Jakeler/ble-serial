import logging, sys, argparse, time, asyncio
from ble_serial.serial.linux_pty import UART
from ble_serial.ble_interface import BLE_interface
from ble_serial.fs_log import FS_log, Direction
from bleak.exc import BleakError

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, 
        description='Create virtual serial ports from BLE devices.')
    
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
        help='Increase verbosity to log all data going through')
    parser.add_argument('-d', '--dev', dest='device', required=True,
        help='BLE device address to connect (hex format, can be seperated by colons)')
    parser.add_argument('-t', '--address-type', dest='addr_type', required=False, choices=['public', 'random'], default='public',
        help='BLE address type, either public or random')
    parser.add_argument('-i', '--interface', dest='adapter', required=False, default='0',
        help='BLE host adapter number to use')
    parser.add_argument('-w', '--write-uuid', dest='write_uuid', required=False,
        help='The GATT chracteristic to write the serial data, you might use "scan.py -d" to find it out')
    parser.add_argument('-l', '--log', dest='filename', required=False,
        help='Enable optional logging of all bluetooth traffic to file')
    parser.add_argument('-b', '--binary', dest='binlog', required=False, action='store_true',
        help='Log data as raw binary, disable transformation to hex. Works only in combination with -l')
    parser.add_argument('-p', '--port', dest='port', required=False, default='/tmp/ttyBLE',
        help='Symlink to virtual serial port')
    parser.add_argument('-r', '--read-uuid', dest='read_uuid', required=False,
        help='The GATT characteristic to subscribe to notifications to read the serial data')
    args = parser.parse_args()

    logging.basicConfig(
        format='%(asctime)s.%(msecs)03d | %(levelname)s | %(filename)s: %(message)s', 
        datefmt='%H:%M:%S',
        level=logging.DEBUG if args.verbose else logging.INFO
    )

    asyncio.run(run(args))


async def run(args):
    loop = asyncio.get_event_loop()
    try:
        uart = UART(args.port, loop)
        bt = BLE_interface()
        if args.filename:
            log = FS_log(args.filename, args.binlog)
            bt.set_receiver(log.middleware(Direction.BLE_IN, uart.write_sync))
            uart.set_receiver(log.middleware(Direction.BLE_OUT, bt.queue_send))
        else:
            bt.set_receiver(uart.write_sync)
            uart.set_receiver(bt.queue_send)

        uart.start()
        await bt.start(args.device, args.addr_type, args.adapter, args.write_uuid, args.read_uuid)
        await bt.send_loop()
        logging.info('Running main loop!')

    except BleakError as e:
        logging.warning(f'Bluetooth connection failed: {e}')
    except KeyboardInterrupt:
        logging.info('Keyboard interrupt received')
    except Exception as e:
        logging.error(f'Unexpected Error: {e}')
    finally:
        logging.warning('Shutdown initiated')
        if 'uart' in locals():
            uart.stop()
        if 'bt' in locals():
            await bt.shutdown()
        if 'log' in locals():
            log.finish()
        logging.info('Shutdown complete.')


if __name__ == '__main__':
    main()