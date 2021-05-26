from bleak import BleakScanner, BleakClient
from bleak.backends.service import BleakGATTServiceCollection
from bleak.exc import BleakError
import argparse, asyncio


async def scan(args):
    if args.addr:
        await deep_scan(args.addr, args.sec)
    else:
        await general_scan(args.sec)

async def general_scan(time: float):
    print("Started BLE scan\n")

    devices = await BleakScanner.discover(timeout=time)

    sorted_devices = sorted(devices, key=lambda dev: dev.rssi, reverse=True)
    for d in sorted_devices:
        print(f'{d.address} (RSSI={d.rssi}): {d.name}')

    print("\nFinished BLE scan")


async def deep_scan(dev: str, time: float):
    print(f"Started deep scan of {dev}\n")

    async with BleakClient(dev, timeout=time) as client:
        print_details(await client.get_services())

    print(f"\nCompleted deep scan of {dev}")

def print_details(serv: BleakGATTServiceCollection):
    INDENT = '    '
    for s in serv:
        print('SERVICE', s)
        for char in s.characteristics:
            print(INDENT, 'CHARACTERISTIC', char, char.properties)
            for desc in char.descriptors:
                print(INDENT*2, 'DESCRIPTOR', desc)


# Extra function for console scripts
def main():
    parser = argparse.ArgumentParser(
        description='Scanner for BLE devices and service/characteristics.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-t', '--scan-time', dest='sec', default=5.0, type=float, 
        help='Duration of the scan in seconds')
    parser.add_argument('-d', '--deep-scan', dest='addr', type=str,
        help='Try to connect to device and read out service/characteristic UUIDs')
    args = parser.parse_args()

    try:
        asyncio.run(scan(args))
    except BleakError as be:
        print('ERROR:', be)

