from ble_serial.ports.interface import ISerial
import asyncio
import logging
import os
import pty
import tty
import termios

class UART(ISerial):
    def __init__(self, symlink: str, ev_loop: asyncio.AbstractEventLoop, mtu: int):
        self.loop = ev_loop
        self.mtu = mtu
        self._send_queue = asyncio.Queue()

        self._controller_fd, endpoint_fd = pty.openpty()
        self.endpoint_path = os.ttyname(endpoint_fd)
        tty.setraw(self._controller_fd, termios.TCSANOW)

        self.symlink = symlink
        os.symlink(self.endpoint_path, self.symlink)
        logging.info(f'Port endpoint created on {self.symlink} -> {self.endpoint_path}')
    
    def set_receiver(self, callback):
        self._cb = callback


    def start(self):
        assert self._cb, 'Receiver must be set before start!'

        # Register the file descriptor for read event
        self.loop.add_reader(self._controller_fd, self.read_handler)

    def stop_loop(self):
        logging.info('Stopping serial event loop')
        self._send_queue.put_nowait(None)

    def remove(self):
        # Unregister the fd
        self.loop.remove_reader(self._controller_fd)
        os.remove(self.symlink)
        logging.info('Serial reader and symlink removed')


    def read_handler(self):
        data = self.read_sync()
        self._cb(data)

    def read_sync(self):
        value = os.read(self._controller_fd, self.mtu)
        logging.debug(f'Read: {value}')
        return value

    def queue_write(self, value: bytes):
        self._send_queue.put_nowait(value)

    async def run_loop(self):
        while True:
            data = await self._send_queue.get()
            if data is None:
                break # Let future end on shutdown
            logging.debug(f'Write: {data}')
            os.write(self._controller_fd, data)
