from bluepy.btle import Scanner, DefaultDelegate, ScanEntry, Peripheral, BTLEException
import argparse

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            print(f"Discovered device: {dev.addr} -> {dev.getValueText(0x9)}")
        elif isNewData:
            print("Received new data from", dev.addr)

def scan(time: float, deep: bool):
    scanner = Scanner().withDelegate(ScanDelegate())
    devices = scanner.scan(time)
    print(f'Found {len(devices)} devices!\n')

    for dev in devices:
        print(f"Device {dev.addr} ({dev.addrType}), RSSI={dev.rssi} dB")
        for (adtype, desc, value) in dev.getScanData():
            print(f"    {adtype:02x}: {desc} = {value}")
        if deep:
            specific_scan(dev)
        print()

def specific_scan(addr: str):
    try:
        dev = Peripheral(deviceAddr=addr)
        print_dev(dev)
        dev.disconnect()
    except BTLEException as e:
        print(f'Could not read device: {e}')

def print_dev(dev):
    serv = dev.getServices()
    for service in serv:
        print('  Service:', service.uuid)
        for char in service.getCharacteristics():
            print('    Characteristic:', char.uuid, char.propertiesToString())

def main():
    parser = argparse.ArgumentParser(
        description='Scanner for BLE devices and service/characteristcs. ROOT required.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-t', '--scan-time', dest='sec', default=5.0, type=float, 
        help='Duration of the scan in seconds')
    parser.add_argument('-d', '--deep-scan', dest='deep', action='store_true',
        help='Try to connect to the devices and read out the service/characteristic UUIDs')
    args = parser.parse_args()

    scan(args.sec, args.deep)

if __name__ == '__main__':
    main()