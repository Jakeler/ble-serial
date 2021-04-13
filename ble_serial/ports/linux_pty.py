from ble_serial.ports.interface import ISerial
import asyncio, logging
import os, pty, tty, termios

class UART(ISerial):
    def __init__(self, symlink: str, ev_loop: asyncio.AbstractEventLoop, mtu: int):
        self.loop = ev_loop
        self.mtu = mtu
        self._send_queue = asyncio.Queue()

        master, slave = pty.openpty()
        tty.setraw(master, termios.TCSANOW)
        self._master = master
        self.endpoint = os.ttyname(slave)

        self.symlink = symlink
        os.symlink(self.endpoint, self.symlink)
        logging.info(f'Slave created on {self.symlink} -> {self.endpoint}')
    
    def set_receiver(self, callback):
        self._cb = callback


    def start(self):
        assert self._cb, 'Receiver must be set before start!'

        # Register the file descriptor for read event
        self.loop.add_reader(self._master, self.read_handler)

    def stop_loop(self):
        logging.info('Stopping serial event loop')
        self._send_queue.put_nowait(None)

    def remove(self):
        # Unregister the fd
        self.loop.remove_reader(self._master)
        os.remove(self.symlink)
        logging.info(f'Serial reader and symlink removed')


    def read_handler(self):
        data = self.read_sync()
        self._cb(data)

    def read_sync(self):
        value = os.read(self._master, self.mtu)
        logging.debug(f'Read: {value}')
        return value

    def queue_write(self, value: bytes):
        self._send_queue.put_nowait(value)

    async def run_loop(self):
        while True:
            data = await self._send_queue.get()
            if data == None:
                break # Let future end on shutdown
            logging.debug(f'Write: {data}')
            os.write(self._master, data)
