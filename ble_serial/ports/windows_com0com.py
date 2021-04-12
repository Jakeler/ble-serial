from ble_serial.ports.interface import ISerial
from ble_serial.setup_com0com.windows_priv_setupc import PORT_INTERNAL
import serial # pyserial

class COM(ISerial):
    def __init__(self):
        self.serial = serial.Serial(f"\\\\.\\{PORT_INTERNAL}")

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

