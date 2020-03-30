import os, pty, tty, termios, logging
from select import select
from threading import Thread

class UART(Thread):
    def __init__(self, symlink: str):
        super(UART, self).__init__()
        self.running = True

        master, slave = pty.openpty()
        tty.setraw(master, termios.TCSANOW)
        self._master = master
        self.endpoint = os.ttyname(slave)
        self.symlink = symlink
        os.symlink(self.endpoint, self.symlink)
        logging.info(f'Slave created on {self.symlink} -> {self.endpoint}')
    
    def set_receiver(self, callback):
        self._cb = callback

    def run(self):
        assert self._cb, 'Receiver must be set before start!'

        while self.running:
            r, _, _ = select([self._master], [], [], 1.0)
            if self._master in r:
                data = self.read_sync()
                self._cb(data)

    def stop(self):
        logging.info('Stopping UART thread')
        self.running = False
        while self.is_alive():
            pass
        os.remove(self.symlink)


    def read_sync(self):
        value = os.read(self._master, 1024)
        logging.debug(f'Read: {value}')
        return value

    def write_sync(self, value: bytes):
        os.write(self._master, value)
        logging.debug(f'Write: {value}')

