from virtual_serial import UART
import logging, time

logging.basicConfig(
    format='%(asctime)s.%(msecs)d | %(levelname)s | %(filename)s: %(message)s', 
    datefmt='%H:%M:%S',
    level=logging.DEBUG
)

if __name__ == '__main__':

    uart = UART()
    while True:
        try:
            uart.write_sync(b'Hello World')
            time.sleep(3)
        except KeyboardInterrupt:
            exit(0)