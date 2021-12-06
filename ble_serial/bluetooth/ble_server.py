from bless import BlessServer, BlessGATTCharacteristic
from bless import GATTAttributePermissions, GATTCharacteristicProperties

import logging, asyncio
from typing import Optional

class BLE_server():
    def __init__(self):
        self._send_queue = asyncio.Queue()
        self.data_read_done = asyncio.Event()

        self.server = BlessServer(name='BLE Serial Server') # loop=asyncio.get_event_loop())
        self.server.read_request_func = self.handle_incoming_read
        self.server.write_request_func = self.handle_incoming_write

    async def start(self, addr_str: str, addr_type: str, adapter: str, timeout: float):
        # logging.info(f'Trying to start with {addr_str}')
        #TODO: obtain adapter address
        success = await self.server.start(timeout=timeout)
        logging.info(f'Server startup {"failed!" if success == False else "successful"}')


    async def setup_chars(self, write_uuid: str, read_uuid: str, mode: str):
        self.read_enabled = 'r' in mode
        self.write_enabled = 'w' in mode

        service_uuid = "0000ffe0-0000-1000-8000-00805f9b34fb"
        await self.server.add_new_service(service_uuid)
        self.service = self.server.get_service(service_uuid)
        logging.info(f'Service {str(self.service)}')

        # TODO: setup depending on mode
        # if self.write_enabled:
        #     self.write_char = self.find_char(write_uuid, ['write', 'write-without-response'])
        # else:
        #     logging.info('Writing disabled, skipping write UUID detection')
        
        # if self.read_enabled:
        #     self.read_char = self.find_char(read_uuid, ['notify', 'indicate'])
        #     await self.dev.start_notify(self.read_char, self.handle_notify)
        # else:
        #     logging.info('Reading disabled, skipping read UUID detection')

        write_uuid = "0000ffe1-0000-1000-8000-00805f9b34fb"
        char_flags = GATTCharacteristicProperties.write | GATTCharacteristicProperties.write_without_response
        permissions =  GATTAttributePermissions.readable | GATTAttributePermissions.writeable
        await self.server.add_new_characteristic(service_uuid, write_uuid,
            char_flags, None, permissions)

        self.write_char = self.server.get_characteristic(write_uuid)
        logging.info(f'Write characteristic: {str(self.write_char)}')

        read_uuid = "0000ffe2-0000-1000-8000-00805f9b34fb"
        char_flags = GATTCharacteristicProperties.read | GATTCharacteristicProperties.notify
        permissions =  GATTAttributePermissions.readable | GATTAttributePermissions.writeable
        await self.server.add_new_characteristic(service_uuid, read_uuid,
            char_flags, None, permissions)

        self.read_char = self.server.get_characteristic(read_uuid)
        logging.info(f'Read characteristic: {str(self.read_char)}')

        self.data_read_done.set()

    def handle_incoming_read(self, char: BlessGATTCharacteristic) -> bytearray:
        logging.debug('Client read data')
        if self.read_char != char:
            logging.warning('Read request received on wrong characteristic')
            return None
        self.data_read_done.set()
        return self.read_char.value

    def queue_send(self, data: bytes):
        self._send_queue.put_nowait(data)

    async def send_loop(self):
        assert hasattr(self, '_cb'), 'Callback must be set before receive loop!'
        while True:
            data = await self._send_queue.get()
            if data == None:
                break # Let future end on shutdown
            if not self.read_enabled:
                logging.warning(f'Ignoring unexpected read data: {data}')
                continue
            logging.debug(f'Offering read {data}')
            # Wait for current data to get read, then overwrite
            # await self.data_read_done.wait()
            self.read_char.value = data
            # Mark as ready to read
            self.data_read_done.clear()
            self.server.update_value(self.service.uuid, self.read_char.uuid)
        await server.stop()

    def stop_loop(self):
        logging.info('Stopping Bluetooth event loop')
        self._send_queue.put_nowait(None)

    async def disconnect(self):
        if hasattr(self, 'server'):
            await self.server.stop()
            logging.info('Bluetooth server stopped')

    def set_receiver(self, callback):
        self._cb = callback
        logging.info('Receiver set up')

    def handle_incoming_write(self, char: BlessGATTCharacteristic, data: bytes):
        logging.debug(f'Received write from {char}: {data}')
        if not self.write_enabled:
            logging.warning(f'Got unexpected write data, dropping: {data}')
            return
        self._cb(data)
