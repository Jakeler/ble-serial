from bluepy.btle import Scanner, DefaultDelegate, ScanEntry

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            print(f"Discovered device: {dev.addr} -> {dev.getValueText(0x9)}")
        elif isNewData:
            print("Received new data from", dev.addr)

scanner = Scanner().withDelegate(ScanDelegate())
devices = scanner.scan(5.0)

for dev in devices:
    print(f"Device {dev.addr} ({dev.addrType}), RSSI={dev.rssi} dB")
    print(dev)
    for (adtype, desc, value) in dev.getScanData():
        print(f"{adtype}: {desc} = {value}")