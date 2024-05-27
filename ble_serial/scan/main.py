from bleak import BleakScanner, BleakClient
from bleak.backends.service import BleakGATTServiceCollection
from bleak.exc import BleakError
import argparse
import asyncio


async def scan(adapter: str, timeout: float, service_uuid: str) -> dict:
    base_kwargs = dict(adapter=adapter, timeout=timeout, return_adv=True)

    if service_uuid:
        devices = await BleakScanner.discover(**base_kwargs, service_uuids=[service_uuid])
    else:
        devices = await BleakScanner.discover(**base_kwargs)

    return devices

async def deep_scan(addr: str, devices: dict) -> BleakGATTServiceCollection:
    devices = [data[0] for data in devices.values()]
    devices = filter(lambda dev: dev.address == addr, devices)
    devices_list = list(devices)
    if len(devices_list) > 0:
        device = devices_list[0]
        print(f'Found device {device} (out of {len(devices_list)})')
    else:
        print('Found no device with matching address')
        return []

    async with BleakClient(device) as client:
        return client.services


def print_list(devices: dict, verbose: bool):
    for (dev, adv) in devices.values():
        print(f'{dev.address} (rssi={adv.rssi}): {dev.name}')
        if verbose:
            for entry_pair in adv._asdict().items():
                print('    %s=%s' % entry_pair)
            print() # linebreak
            


def print_details(serv: BleakGATTServiceCollection):
    INDENT = '    '
    for s in serv:
        print('SERVICE', s)
        for char in s.characteristics:
            print(INDENT, 'CHARACTERISTIC', char, char.properties)
            for desc in char.descriptors:
                print(INDENT*2, 'DESCRIPTOR', desc)


async def run_from_args(args):
    print("Started general BLE scan\n")
    devices = await scan(args.adapter, args.sec, args.service_uuid)
    if len(devices) == 0:
        print('No devices found')
        return # no point in finishing / deep scan
    print_list(devices, args.verbose)
    print("\nFinished general BLE scan")

    if args.addr:
        print(f"\nStarted deep scan of {args.addr}\n")
        services = await deep_scan(args.addr, devices)
        print_details(services)
        print(f"\nCompleted deep scan of {args.addr}")


# Extra function for console scripts
def launch():
    parser = argparse.ArgumentParser(
        description='Scanner for BLE devices and service/characteristics.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-t', '--scan-time', dest='sec', default=5.0, type=float, 
        help='Duration of the scan in seconds')
    parser.add_argument('-i', '--interface', dest='adapter', required=False, default='hci0',
        help='BLE host adapter number to use')
    parser.add_argument('-d', '--deep-scan', dest='addr', type=str,
        help='Try to connect to device and read out service/characteristic UUIDs')
    parser.add_argument('-s', '--service-uuid', dest='service_uuid', required=False,
        help='The service used for scanning of potential devices')
    parser.add_argument('-v', '--verbose', dest='verbose', required=False, action='store_true',
        help='Print all infos from advertisement data')
    args = parser.parse_args()

    try:
        asyncio.run(run_from_args(args))
    except BleakError as be:
        print('ERROR:', be)

