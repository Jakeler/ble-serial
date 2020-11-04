from bluepy.btle import Peripheral, Characteristic, Service, UUID
from bluepy.btle import DefaultDelegate, BTLEException
import logging
from ble_serial.constants import ble_chars

class BLE_interface():
    def __init__(self, addr_str, addr_type, adapter, write_uuid, read_uuid,):
        self.dev = Peripheral(deviceAddr=addr_str, addrType=addr_type, iface=adapter)
        logging.info(f'Connected device {self.dev.addr}')

        if write_uuid:
            self.write_uuid = [UUID(write_uuid)]
        else:
            self.write_uuid = [UUID(x) for x in ble_chars]
            logging.debug(f'No write uuid specified, trying {ble_chars}')
        for c in self.dev.getCharacteristics():
            if c.uuid in self.write_uuid:
                self._write_charac = c
                self.write_uuid = self._write_charac.uuid
                logging.debug(f'Found write characteristic {self.write_uuid}')
                break
        assert hasattr(self, '_write_charac'), \
            "No characteristic with specified UUID found!"
        assert (self._write_charac.properties & Characteristic.props["WRITE_NO_RESP"]), \
            "Specified characteristic is not writable!"

        # Only subscribe to read_uuid notifications if it was specified
        if read_uuid:
            self.read_uuid = [UUID(read_uuid)]
            for c in self.dev.getCharacteristics():
                if c.uuid in self.read_uuid:
                    self._read_charac = c
                    self.read_uuid = self._read_charac.uuid
                    logging.debug(f'Found read characteristic {self.read_uuid}')
                    break
            assert hasattr(self, '_read_charac'), \
                "No read characteristic with specified UUID found!"
            assert (self._read_charac.properties & Characteristic.props["NOTIFY"]), \
                "Specified read characteristic is not notifiable!"
            # Attempt to subscribe to notification now (write CCCD)
            # First get the Client Characteristic Configuration Descriptor
            self._read_charac_cccd = self._read_charac.getDescriptors(0x2902)
            assert (self._read_charac_cccd is not None), \
                "Could not find CCCD for given read UUID!"
            self._read_charac_cccd = self._read_charac_cccd[0]
            # Now write that we want notifications from this UUID
            self._read_charac_cccd.write(bytes([0x01, 0x00]))

    def send(self, data: bytes):
        logging.debug(f'Sending {data}')
        self._write_charac.write(data, withResponse=False)

    def set_receiver(self, callback):
        logging.info('Receiver set up')
        self.dev.setDelegate(ReceiverDelegate(callback))

    def receive_loop(self):
        assert isinstance(self.dev.delegate, ReceiverDelegate), 'Callback must be set before receive loop!'
        self.dev.waitForNotifications(3.0)

    def shutdown(self):
        self.dev.disconnect()
        logging.info('BT disconnected')


class ReceiverDelegate(DefaultDelegate):
    def __init__(self, callback):
        self._cb = callback
    
    def handleNotification(self, handle, data):
        logging.debug(f'Received notify: {data}')
        self._cb(data)