from ble_serial.ports.interface import ISerial
from ble_serial.setup_com0com.windows_priv_setupc import PORT_INTERNAL
import asyncio, logging
from serial import Serial # pyserial
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor

class COM(ISerial):
    def __init__(self, _, ev_loop: asyncio.AbstractEventLoop, mtu: int):
        self.alive = True # to stop executor threads
        self.loop = ev_loop
        self.mtu = mtu
        self.tx_queue = Queue()

    def start(self):
        self.serial = Serial(f"\\\\.\\{PORT_INTERNAL}")

    def set_receiver(self, callback):
        self._cb = callback

    def queue_write(self, value: bytes):
        self.tx_queue.put(value)

    async def run_loop(self):
        pool = ThreadPoolExecutor(max_workers=2)
        rx = self.loop.run_in_executor(pool, self._run_rx)
        tx = self.loop.run_in_executor(pool, self._run_tx)
        return asyncio.gather(rx, tx)

    def _run_tx(self):
        while self.alive and self.serial.is_open:
            try:
                data = self.tx_queue.get(block=True, timeout=3)
                logging.debug(f'Write: {data}')
                self.serial.write(data)
            except Empty as e:
                logging.debug('TX queue timeout: was empty')

        logging.debug(f'TX loop ended {self.alive=} {self.serial.is_open=}')
    
    def _run_rx(self):
        # based on ReaderThread(threading.Thread) from:
        # https://github.com/pyserial/pyserial/blob/master/serial/threaded/__init__.py
        while self.alive and self.serial.is_open:
            n = min(self.mtu, self.serial.in_waiting) or 1 # request at least 1 to block
            data = self.serial.read(n)
            logging.debug(f'Read: {data}')
            self.loop.call_soon_threadsafe(self._cb, data) # needed as asyncio.Queue is not thread safe

        logging.debug(f'RX loop ended {self.alive=} {self.serial.is_open=}')

    def stop_loop(self):
        self.alive = False
        logging.info('Stopping RX+TX loop')

    def remove(self):
        self.serial.close()

