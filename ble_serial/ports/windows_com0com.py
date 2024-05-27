from ble_serial.ports.interface import ISerial
import asyncio
import logging
from serial import Serial # pyserial
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor

class COM(ISerial):
    def __init__(self, port: str, ev_loop: asyncio.AbstractEventLoop, mtu: int):
        self.alive = True # to stop executor threads
        self.loop = ev_loop
        self.mtu = mtu
        self.port = port
        self.tx_queue = Queue()

    def start(self):
        self.serial = Serial(f"\\\\.\\{self.port}")

    def set_receiver(self, callback):
        self._cb = callback

    def queue_write(self, value: bytes):
        self.tx_queue.put(value)

    async def run_loop(self):
        pool = ThreadPoolExecutor(max_workers=2)
        rx = self.loop.run_in_executor(pool, self._run_rx)
        tx = self.loop.run_in_executor(pool, self._run_tx)
        main = self._run_main_thread()
        await asyncio.gather(main, rx, tx)

    def _run_tx(self):
        while self.alive:
            try:
                data = self.tx_queue.get(block=True, timeout=3)
                logging.debug(f'Write: {data}')
                self.serial.write(data)
            except Empty as e:
                logging.debug('TX queue timeout: was empty')

        logging.debug(f'TX loop ended alive={self.alive} open={self.serial.is_open}')
    
    def _run_rx(self):
        # based on ReaderThread(threading.Thread) from:
        # https://github.com/pyserial/pyserial/blob/master/serial/threaded/__init__.py
        while self.alive:
            data = self.serial.read(1) # request 1 to block
            n = min(self.mtu - 1, self.serial.in_waiting) # read the remaning, can be 0
            data += self.serial.read(n)
            logging.debug(f'Read: {data}')
            self.loop.call_soon_threadsafe(self._cb, data) # needed as asyncio.Queue is not thread safe

        logging.debug(f'RX loop ended, alive={self.alive} open={self.serial.is_open}')

    async def _run_main_thread(self):
        # Dummy work in main thread, it has to run to detect signals (e.g. ctrl-C)
        # https://stackoverflow.com/a/29237343
        # we can also use it to check if the serial is still open, instead of doing that in every thread
        while self.alive:
            self.alive = False if not self.serial.is_open else self.alive
            await asyncio.sleep(0.5)


    def stop_loop(self):
        self.alive = False
        logging.info('Stopping RX+TX loop')

    def remove(self):
        if hasattr(self, 'serial'):
            self.serial.close()
            self.stop_loop()

