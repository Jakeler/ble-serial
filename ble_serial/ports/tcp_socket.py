from ble_serial.ports.interface import ISerial
import asyncio
import logging


class TCP_Socket(ISerial):
    def __init__(self, host: str, port: int, mtu: int):
        logging.debug(f'{host=}:{port=}, {mtu=}')
        self.host = host
        self.port = port
        self.mtu = mtu
        self.connected = False

    def set_receiver(self, callback):
        self._cb = callback

    def queue_write(self, value: bytes):
        if self.connected:
            logging.debug(f'Sending: {value}')
            self.writer.write(value)
        else:
            logging.debug('No client connected, dropping data...')

    def handle_connect(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        logging.info(f'New TCP peer connected: {writer.get_extra_info("peername")}')
        if self.connected:
            logging.warning('More than one connection is not allowed, closing')
            writer.close()
            return
        self.writer = writer
        self.reader = reader
        self.connected = True


    async def run_loop(self):
        server =  await asyncio.start_server(
            self.handle_connect, self.host, self.port)

        logging.info('TCP server started' if server.is_serving() else 'TCP server failed')
        for sock in server.sockets:
            logging.debug(f'Listening on {sock}')

        while True:
            if self.connected:
                try:
                    data = await self.reader.read(self.mtu)
                except OSError as ose:
                    logging.warning(f'Client disconnected: {ose}')
                    self.connected = False
                    continue

                if len(data) > 0:
                    logging.debug(f'Received {data}')
                    self._cb(data)
                else:
                    logging.warning('Client disconnected (EOF)')
                    self.connected = False
            else:
                await asyncio.sleep(3)
                logging.debug('Waiting for client connection')

    def start(self):
        pass

    def stop_loop(self):
        pass

    def remove(self):
        pass