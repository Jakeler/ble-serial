from bluepy.btle import Peripheral, Characteristic, Service, UUID
from bluepy.btle import DefaultDelegate, BTLEException

class ReceiverDelegate(DefaultDelegate):
    def handleNotification(self, data):
        print(data)

def showDevInfo(dev):
    serv = dev.getServices()
    for service in serv:
        print('Service', service.uuid)
        for char in service.getCharacteristics():
            print('Characteristic', char.uuid, char.propertiesToString())

def shutdown():
    print('Shutting down...')
    dev.disconnect()
    exit(0)

addr_str = '20:91:48:4c:4c:54'
dev = Peripheral(deviceAddr=addr_str)
print(dev.status())
showDevInfo(dev)


dev.setDelegate(ReceiverDelegate)
while True:
    try:
        dev.waitForNotifications(1.0)
    except BTLEException:
        shutdown()
    except KeyboardInterrupt:
        shutdown()