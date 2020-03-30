import logging, sys, argparse, time
from ble_serial.virtual_serial import UART
from ble_serial.interface import BLE_interface
from ble_serial.fs_log import FS_log, Direction
from bluepy.btle import BTLEDisconnectError

def main():
    parser = argparse.ArgumentParser(description='Create virtual serial ports from BLE devices.')
    parser.add_argument('-v', dest='verbose', action='store_true',
        help='Increase verbosity (logs all data going through)')
    parser.add_argument('-d', '--dev', dest='device', required=True,
        help='BLE device address to connect (hex format, can be seperated by colons)')
    parser.add_argument('-w', '--write-uuid', dest='write_uuid', required=False,
        help='The GATT chracteristic to write the serial data, you might use "scan.py -d" to find it out')
    parser.add_argument('-l', '--log', dest='filename', required=False,
        help='Enable optional logging of all bluetooth traffic to file')
    parser.add_argument('-p', '--port', dest='port', required=False, default='/tmp/ttyBLE',
        help='Symlink to virtual serial port (default = /tmp/ttyBLE)')
    args = parser.parse_args()

    logging.basicConfig(
        format='%(asctime)s.%(msecs)d | %(levelname)s | %(filename)s: %(message)s', 
        datefmt='%H:%M:%S',
        level=logging.DEBUG if args.verbose else logging.INFO
    )

    try:
        uart = UART(args.port)
        bt = BLE_interface(args.device, args.write_uuid)
        if args.filename:
            log = FS_log(args.filename)
            bt.set_receiver(log.middleware(Direction.BLE_IN, uart.write_sync))
            uart.set_receiver(log.middleware(Direction.BLE_OUT, bt.send))
        else:
            bt.set_receiver(uart.write_sync)
            uart.set_receiver(bt.send)
        logging.info('Running main loop!')
        uart.start()
        while True:
            bt.receive_loop()
    except BTLEDisconnectError:
        logging.warning('Bluetooth connection lost')
    except KeyboardInterrupt:
        logging.info('Keyboard interrupt received')
    except Exception as e:
        logging.error(f'Unexpected Error: {e}')
    finally:
        logging.warning('Shutdown initiated')
        if 'uart' in locals():
            uart.stop()
        if 'bt' in locals():
            bt.shutdown()
        if args.filename:
            log.finish()
        logging.info('Shutdown complete.')
        exit(0)

if __name__ == '__main__':
    main()