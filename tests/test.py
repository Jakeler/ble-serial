from concurrent.futures import ThreadPoolExecutor as TPE
import csv
from time import sleep

from hm11_at_config import set_module_baud
from serial_handler import read_serial, write_serial, run_ble_serial, signal_serial_end

# Interfaces
PORT_UART = '/dev/ttyUSB0'
PORT_BLE = '/tmp/ttyBLE'

with open('../README.md', 'rb') as f:
    CONTENT = f.read()
    # print(CONTENT)

# CONTENT = CONTENT[:1000]

class Dir:
    _ports = [
        (PORT_BLE, PORT_UART),
        (PORT_UART, PORT_BLE),
    ]

    @classmethod
    def BLE_UART(cls):
        return cls(0)

    @classmethod
    def UART_BLE(cls):
        return cls(1)

    def __init__(self, dir: int):
        self.id = dir
        self.write = self._ports[dir][0]
        self.read = self._ports[dir][1]

    def __str__(self):
        return ('BLE >> UART', 'UART >> BLE')[self.id]

class Log:
    def __init__(self, filename: str):
        fieldnames = ['dir', 'rated_baud', 'packet_size', 'delay', 
            'valid', 'loss_percent', 'rx_bits', 'rx_baud']
        self.csvfile = open(filename, 'w', newline='')
        self.writer = csv.DictWriter(self.csvfile, fieldnames=fieldnames)
        self.writer.writeheader()

    def write(self, data: dict):
        self.writer.writerow(data)

    def close(self):
        self.csvfile.close()

def run_test(exc: TPE, log: Log, dir: Dir, baud: int, packet_size: int, delay: float):
    futw = executor.submit(write_serial, dir.write, baud, CONTENT, packet_size, delay)
    futr = executor.submit(read_serial, dir.read, baud, CONTENT)

    result = futr.result()
    result.update({
        'dir': str(dir),
        'rated_baud': baud,
        'packet_size': packet_size,
        'delay': delay,
    })
    log.write(result)
    print(result, end='\n\n')


baud_to_test = [9600, 19200, 57600, 115200, 230400]
prev = baud_to_test[0]

# PACKET_SIZE = [4, 16, 64]
PACKET_SIZE = [32]
BYTE_DELAY = [0, 1/2000, 1/1000, 1/500] # bytes/sec

if __name__ == "__main__":
    # Reset to start baud after fail
    # set_module_baud(PORT_UART, 19200, 9600)
    # os.remove(PORT_BLE)

    log = Log('results/log.csv')

    for baud in baud_to_test:
        print(f'\nTesting baud: {baud}')

        set_module_baud(PORT_UART, prev, baud)
        prev = baud

        with TPE(max_workers=3) as executor:
            futb = executor.submit(run_ble_serial)
            sleep(3)

            for size in PACKET_SIZE:
                for delay in BYTE_DELAY:
                    run_test(executor, log, Dir.BLE_UART(), baud, size, size*delay)
                    run_test(executor, log, Dir.UART_BLE(), baud, size, size*delay)

            signal_serial_end()

    set_module_baud(PORT_UART, prev, baud_to_test[0])
    log.close()
