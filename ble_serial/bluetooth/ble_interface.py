from bleak import BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.exc import BleakError
from ble_serial.bluetooth.constants import ble_chars
import logging, asyncio
from typing import Optional

class BLE_interface():
    async def start(self, addr_str, addr_type, adapter, timeout, write_uuid, read_uuid,):
        self._send_queue = asyncio.Queue()

        # address_type used only in Windows .NET currently
        self.dev = BleakClient(addr_str, adapter=adapter, address_type=addr_type, timeout=timeout)
        self.dev.set_disconnected_callback(self.handle_disconnect)

        logging.info(f'Trying to connect with {addr_str}')
        await self.dev.connect()
        logging.info(f'Device {self.dev.address} connected')

        self.write_char = self.find_char(write_uuid, ['write', 'write-without-response'])
        self.read_char = self.find_char(read_uuid, ['notify'])

        await self.dev.start_notify(self.read_char, self.handle_notify)

    def find_char(self, uuid: Optional[str], req_props: [str]) -> BleakGATTCharacteristic:
        name = req_props[0]

        # Use user supplied UUID first, otherwise try included list
        if uuid:
            uuid_candidates = [uuid]
        else:
            uuid_candidates = ble_chars
            logging.debug(f'No {name} uuid specified, trying builtin list')

        results = []
        for srv in self.dev.services:
            for c in srv.characteristics:
                if c.uuid in uuid_candidates:
                    results.append(c)

        assert len(results) > 0, \
            f"No characteristic with specified UUID {uuid_candidates} found!"

        res_str = '\n'.join(f'\t{c} {c.properties}' for c in results)
        logging.debug(f'Characteristic candidates for {name}: \n{res_str}')

        # Check if there is a intersection of permission flags
        results[:] = [c for c in results if set(c.properties) & set(req_props)]

        assert len(results) > 0, \
            f"No characteristic with {req_props} property found!"

        assert len(results) == 1, \
            f'Multiple matching {name} characteristics found, please specify one'

        # must be valid here
        found = results[0]
        logging.info(f'Found {name} characteristic {found.uuid} (H. {found.handle})')
        return found

    def set_receiver(self, callback):
        self._cb = callback
        logging.info('Receiver set up')

    async def send_loop(self):
        assert hasattr(self, '_cb'), 'Callback must be set before receive loop!'
        while True:
            data = await self._send_queue.get()
            if data == None:
                break # Let future end on shutdown
            logging.debug(f'Sending {data}')
            await self.dev.write_gatt_char(self.write_char, data)

    def stop_loop(self):
        logging.info('Stopping Bluetooth event loop')
        self._send_queue.put_nowait(None)

    async def disconnect(self):
        if hasattr(self, 'dev') and self.dev.is_connected:
            if hasattr(self, 'read_char'):
                await self.dev.stop_notify(self.read_char)
            await self.dev.disconnect()
            logging.info('Bluetooth disconnected')

    def queue_send(self, data: bytes):
        self._send_queue.put_nowait(data)

    def handle_notify(self, handle: int, data: bytes):
        logging.debug(f'Received notify from {handle}: {data}')
        self._cb(data)

    def handle_disconnect(self, client: BleakClient):
        logging.warning(f'Device {client.address} disconnected')
        raise BleakError(f'{client.address} disconnected!')