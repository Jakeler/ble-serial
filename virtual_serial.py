import os, pty, logging

class UART:
    def __init__(self):
        master, slave = pty.openpty()
        self._master = master
        self.endpoint = os.ttyname(slave)
        logging.info(f'Slave {self.endpoint}')

    def read_sync(self):
        value = os.read(self._master, 1024)
        logging.debug(f'Read: {value}')
        return value

    def write_sync(self, value: bytes):
        os.write(self._master, value)
        logging.debug(f'Write: {value}')

