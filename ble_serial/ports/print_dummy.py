from ble_serial.ports.interface import ISerial
import asyncio

TEST_DATA = b'Test UART out\n'

class Dummy(ISerial):
    def __init__(self, symlink: str, ev_loop: asyncio.AbstractEventLoop, mtu: int):
        print(f'{symlink=} {mtu=}')
        pass

    def start(self):
        pass

    def set_receiver(self, callback):
        self._cb = callback
        pass

    def queue_write(self, value: bytes):
        print(f'Dummy write queue: {value}')

    async def run_loop(self):
        while True:
            await asyncio.sleep(5)
            self._cb(TEST_DATA)
            print(f'Dummy read callback: {TEST_DATA}')

    def stop_loop(self):
        pass

    def remove(self):
        pass