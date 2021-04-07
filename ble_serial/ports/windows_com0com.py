from ble_serial.ports.interface import ISerial
from ble_serial.ports.windows_priv_setupc import PORT_INTERNAL
import serial

class COM(ISerial):
    def __init__(self):
        self.serial = serial.Serial("\\\\.\\BLE")

    def start(self):
        pass

    def set_receiver(self, callback):
        pass

    def queue_write(self, value: bytes):
        pass

    async def run_loop(self):
        pass

    def stop_loop(self):
        pass

    def remove(self):
        pass

