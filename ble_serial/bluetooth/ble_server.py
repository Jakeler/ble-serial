from bless import BlessServer, BlessGATTCharacteristic
from bless import GATTAttributePermissions, GATTCharacteristicProperties
from ble_serial.bluetooth.interface import BLE_interface
import os, logging, asyncio
from typing import Optional

class BLE_server(BLE_interface):
    def __init__(self, adapter: str, service_uuid: str, write_uuid: str, read_uuid: str):
        self._send_queue = asyncio.Queue()
        self.data_read_done = asyncio.Event()

        self.adapter = adapter # unused / not implemented in bless
        self.service_uuid = service_uuid
        self.write_uuid = write_uuid
        self.read_uuid = read_uuid
        
        # Workaround for bluez not sending constant names, PID always changes
        local_name = f'BLE Serial Server {os.getpid()}'
        logging.debug(f'Name/ID: {local_name}')

        self.server = BlessServer(name=local_name) # loop=asyncio.get_event_loop())
        self.server.read_request_func = self.handle_incoming_read
        self.server.write_request_func = self.handle_incoming_write

    async def start(self, timeout: float):
        # logging.info(f'Trying to start with {addr_str}')
        #TODO: obtain adapter address
        success = await self.server.start(timeout=timeout)
        logging.info(f'Server startup {"failed!" if success == False else "successful"}')


    async def setup_chars(self, mode: str):
        self.read_enabled = 'r' in mode
        self.write_enabled = 'w' in mode

        await self.server.add_new_service(self.service_uuid)
        self.service = self.server.get_service(self.service_uuid)
        logging.info(f'Service {str(self.service)}')

        if self.write_enabled:
            # self.write_uuid = "0000ffe1-0000-1000-8000-00805f9b34fb"
            char_flags = GATTCharacteristicProperties.write | GATTCharacteristicProperties.write_without_response
            permissions = GATTAttributePermissions.readable | GATTAttributePermissions.writeable
            await self.server.add_new_characteristic(self.service_uuid, self.write_uuid,
                char_flags, None, permissions)

            self.write_char = self.server.get_characteristic(self.write_uuid)
            logging.info(f'Write characteristic: {str(self.write_char)}')
        else:
            logging.info('Writing disabled, no characteristic to setup')
        
        if self.read_enabled:
            char_flags = GATTCharacteristicProperties.read | GATTCharacteristicProperties.notify
            permissions = GATTAttributePermissions.readable | GATTAttributePermissions.writeable
            await self.server.add_new_characteristic(self.service_uuid, self.read_uuid,
                char_flags, None, permissions)

            self.read_char = self.server.get_characteristic(self.read_uuid)
            logging.info(f'Read characteristic: {str(self.read_char)}')

            self.data_read_done.set()
        else:
            logging.info('Reading disabled, no characteristic to setup')


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
        logging.info('Listener set up')

    def handle_incoming_write(self, char: BlessGATTCharacteristic, data: bytes):
        logging.debug(f'Received write from {char}: {data}')
        if not self.write_enabled:
            logging.warning(f'Got unexpected write data, dropping: {data}')
            return
        self._cb(data)
