from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.exc import BleakError
from ble_serial.bluetooth.constants import ble_chars
import logging, asyncio
from typing import Optional

class BLE_interface():
    def __init__(self, adapter: str, service: str):
        self._send_queue = asyncio.Queue()

        self.scan_args = dict(adapter=adapter)
        if service:
            self.scan_args['service_uuids'] = [service]

    async def connect(self, addr_str: str, addr_type: str, timeout: float):
        if addr_str:
            device = await BleakScanner.find_device_by_address(addr_str, timeout=timeout, **self.scan_args)
        else:
            logging.warning(f'Picking first device with matching service, '
                'consider passing a specific device address, especially if there could be multiple devices')
            device = await BleakScanner.find_device_by_filter(lambda dev, ad: True, timeout=timeout, **self.scan_args)

        assert device, f'No matching device found!'

        # address_type used only in Windows .NET currently
        self.dev = BleakClient(device, address_type=addr_type, timeout=timeout)
        self.dev.set_disconnected_callback(self.handle_disconnect)

        logging.info(f'Trying to connect with {device}')
        await self.dev.connect()
        logging.info(f'Device {self.dev.address} connected')

    async def setup_chars(self, write_uuid: str, read_uuid: str, mode: str):
        self.read_enabled = 'r' in mode
        self.write_enabled = 'w' in mode

        if self.write_enabled:
            self.write_char = self.find_char(write_uuid, ['write', 'write-without-response'])
        else:
            logging.info('Writing disabled, skipping write UUID detection')
        
        if self.read_enabled:
            self.read_char = self.find_char(read_uuid, ['notify', 'indicate'])
            await self.dev.start_notify(self.read_char, self.handle_notify)
        else:
            logging.info('Reading disabled, skipping read UUID detection')

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

        if uuid:
            assert len(results) > 0, \
                f"No characteristic with specified {name} UUID {uuid} found!"
        else:
            assert len(results) > 0, \
                f"""No characteristic in builtin {name} list {uuid_candidates} found!
                    Please specify one with {'-w/--write-uuid' if name == 'write' else '-r/--read-uuid'}, see also --help"""

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
            if not self.write_enabled:
                logging.warning(f'Ignoring unexpected write data: {data}')
                continue
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
        if not self.read_enabled:
            logging.warning(f'Read unexpected data, dropping: {data}')
            return
        self._cb(data)

    def handle_disconnect(self, client: BleakClient):
        logging.warning(f'Device {client.address} disconnected')
        self.stop_loop()