from ble_serial.serial.interface import ISerial
from ble_serial.serial.windows_priv_setupc import PORT_INTERNAL
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

def run_setup():
    import ctypes, sys, os

    script_path = os.path.dirname(__file__)
    res = ctypes.windll.shell32.ShellExecuteW(None, "runas", 
        sys.executable, f'{script_path}\\windows_priv_setupc.py', None, 1)
    print('OK' if res == 42 else 'Error: higher privileges required')

if __name__ == "__main__":
    run_setup()