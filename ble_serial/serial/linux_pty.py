import asyncio, logging
import os, pty, tty, termios

class UART():
    def __init__(self, symlink: str, ev_loop: asyncio.AbstractEventLoop):
        self.loop = ev_loop

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

        logging.info('Starting UART event loop')
        # Register the file descriptor for read event
        self.loop.add_reader(self._master, self.read_handler)

    def stop(self):
        logging.info('Stopping UART event loop')
        # Unregister the fd
        self.loop.remove_reader(self._master)
        os.remove(self.symlink)


    def read_handler():
        data = self.read_sync()
        self._cb(data)

    def read_sync(self):
        value = os.read(self._master, 255)
        logging.debug(f'Read: {value}')
        return value

    def write_sync(self, value: bytes):
        os.write(self._master, value)
        logging.debug(f'Write: {value}')
