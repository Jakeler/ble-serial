import asyncio
from ble_serial.scan import main as scanner

async def main():
    ### general scan
    ADAPTER = "hci0"
    SCAN_TIME = 5 #seconds
    SERVICE_UUID = None # optional filtering
    VERBOSE = False

    devices = await scanner.scan(ADAPTER, SCAN_TIME, SERVICE_UUID)

    print() # newline
    scanner.print_list(devices, VERBOSE)

    # manual indexing of devices dict
    dev_list = list(devices.values())
    print(dev_list[0])

    ### deep scan get's services/characteristics
    DEVICE = "20:91:48:4C:4C:54"
    services = await scanner.deep_scan(DEVICE, devices)

    scanner.print_details(services)
    print() # newline

    # manual indexing by uuid
    print(services.get_service('0000ffe0-0000-1000-8000-00805f9b34fb'))
    print(services.get_characteristic('0000ffe1-0000-1000-8000-00805f9b34fb'))
    # or by handle
    print(services.services[16])
    print(services.characteristics[17])



if __name__ == "__main__":
    asyncio.run(main())