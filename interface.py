from bluepy.btle import Peripheral, Characteristic, Service, UUID
from bluepy.btle import DefaultDelegate, BTLEException
import logging

class BLE_interface():
    def __init__(self, addr_str):
        self.dev = Peripheral(deviceAddr=addr_str)
        status = self.dev.status()
        logging.debug(status)
        logging.info(f'Device {addr_str} state change to {status["state"][0]}')

    def printDevInfo(self):
        serv = self.dev.getServices()
        for service in serv:
            print('Service', service.uuid)
            for char in service.getCharacteristics():
                print('Characteristic', char.uuid, char.propertiesToString())

    def set_receiver(self, callback):
        logging.info('Receiver set up')
        self.dev.setDelegate(ReceiverDelegate(callback))

    def receive_loop(self):
        assert isinstance(self.dev.delegate, ReceiverDelegate), 'Callback must be set before receive loop!'
        self.dev.waitForNotifications(1.0)

    def shutdown(self):
        self.dev.disconnect()
        logging.info('Shutting down...')


class ReceiverDelegate(DefaultDelegate):
    def __init__(self, callback):
        self._cb = callback
    
    def handleNotification(self, handle, data):
        logging.debug(f'Received notify: {data}')
        self._cb(data)