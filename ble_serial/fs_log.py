import logging, datetime
from enum import Enum

class Direction:
    BLE_IN = "-> BLE-IN"
    BLE_OUT = "<- BLE-OUT"

class FS_log:
    def __init__(self, filename):
        self.file = open(filename, "a+", buffering=1)
        logging.info(f'Logging transfered data to {filename=}')

    def middleware(self, dir: Direction, passthrough_func):
        def ret_func(data):
            passthrough_func(data)
            t = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            self.file.write(f'{t} {dir}: {data.hex(" ")}\n')
        return ret_func

    def finish(self):
        self.file.close()
        logging.info(f'Logfile closed')