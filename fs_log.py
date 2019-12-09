import logging
from enum import Enum

class Direction:
    BLE_IN = "-> BLE-IN"
    BLE_OUT = "<- BLE-OUT"

class FS_log:
    def __init__(self, filename):
        self.file = open(filename, "w+")
        logging.info(f'Logging transfered data to {filename=}')

    def middleware(self, dir: Direction, passthrough_func):
        def ret_func(data):
            passthrough_func(data)
            self.file.write(f'{dir}: Hex: {data.hex("_")}\t Bytes: {data} \n')
        return ret_func

    def finish(self):
        self.file.close()