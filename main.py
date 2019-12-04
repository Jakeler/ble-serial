from virtual_serial import UART
from interface import BLE_interface
from bluepy.btle import BTLEException
import logging, time

logging.basicConfig(
    format='%(asctime)s.%(msecs)d | %(levelname)s | %(filename)s: %(message)s', 
    datefmt='%H:%M:%S',
    level=logging.DEBUG
)

addr_str = '20:91:48:4c:4c:54'

if __name__ == '__main__':
    uart = UART()
    bt = BLE_interface(addr_str)
    bt.set_receiver(uart.write_sync)

    logging.info('Running main loop!')
    while True:
        try:
            # uart.write_sync(b'Hello World')
            bt.receive_loop()
        except KeyboardInterrupt:
            exit(0)
        except BTLEException:
            bt.shutdown()
            exit(1)