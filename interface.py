from bluepy.btle import Peripheral, Characteristic, Service, UUID
from bluepy.btle import DefaultDelegate, BTLEException
import logging

class BLE_interface():
    def __init__(self, addr_str, write_uuid):
        self.dev = Peripheral(deviceAddr=addr_str)
        logging.info(f'Connected device {self.dev.addr}')

        self.write_uuid = UUID(write_uuid)
        for c in self.dev.getCharacteristics():
            if c.uuid == self.write_uuid:
                self._write_charac = c
                logging.debug(f'Found write characteristic {self._write_charac.uuid}')
                break
        assert hasattr(self, '_write_charac'), \
            "No characteristic with specified UUID found!"
        assert (self._write_charac.properties & Characteristic.props["WRITE_NO_RESP"]), \
            "Specified characteristic is not writable!"

        ### Status does not work with patches for wr response with threads...
        # status = self.dev.status()
        # logging.debug(status)
        # logging.info(f'Device {addr_str} state change to {status["state"][0]}')

    def printDevInfo(self):
        serv = self.dev.getServices()
        for service in serv:
            print('Service', service.uuid)
            for char in service.getCharacteristics():
                print('Characteristic', char.uuid, char.propertiesToString())

    def send(self, data):
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