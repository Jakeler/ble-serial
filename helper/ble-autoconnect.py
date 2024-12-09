"""Bluetooth LE automated connections:
Uses bleak to check if devices exist, implementation is cross platform.
It does automatically connect and start the specified tool (for example ble-serial),
if a known device is found. See `autoconnect.ini` for configuration.
"""

import asyncio
from bleak import BleakScanner
from bleak.backends.device import BLEDevice
import signal
import argparse
import configparser
import logging

async def run_tool(conf_section: dict, lock_id: str):
    logging.info(f'{locked_devices}')
    if lock_id in locked_devices:
        return # already running for this device
    
    locked_devices.append(lock_id)
    loop.create_task(pause_scan(args.timeout))

    params = [conf_section['executable']] # binary name before args
    for key, val in conf_section.items():
        if key != 'executable': # add dashes to args
            params.append(f'--{key}')
            if val:
                params.append(val)
    logging.info(params)

    # Run target, passthrough stdout/stderr
    proc = await asyncio.subprocess.create_subprocess_exec(*params)
    await proc.communicate()
    logging.info(f'-> target exit code: {proc.returncode}')

    # Restart scanner
    locked_devices.remove(lock_id)


def detection_callback(device: BLEDevice, adv_data):
    logging.info(f'{device.address} = {adv_data.local_name} (RSSI: {adv_data.rssi}) Services={adv_data.service_uuids}')

    if device.address in config:
        section = config[device.address]
        logging.info(f'Found {device.address} in config!')
        if int(adv_data.rssi) <= args.min_rssi:
            logging.info('Ignoring device because of low rssi')
            return # device not actually availible
        loop.create_task(run_tool(section, device.address))
    else:
        logging.debug('-> Unknown device')

# Pause is needed to receive the advertisment in the recently started ble-serial otherwise autoconnect captures all
async def pause_scan(secs: int):
    await scanner.stop()
    await asyncio.sleep(secs)
    await scanner.start()

def stop(signal, stackframe=None):
    logging.warning(f'signal {signal} received. Stopping scan!')
    loop.create_task(scanner.stop())
    loop.stop()

async def start_scan():
    await scanner.start()

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, 
            description='Service to automatically connect with devices that get available.')
    parser.add_argument('-c', '--config', default='autoconnect.ini', required=False,
            help='Path to a INI file with device configs')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
            help='Increase log level from info to debug')
    parser.add_argument('-m', '--min-rssi', dest='min_rssi', default=-127, type=int,
            help='Ignore devices with weaker signal strength')
    parser.add_argument('-t', '--timeout', dest='timeout', default=10, type=int,
            help='Pause scan for seconds amount to let ble-serial start up')
    args = parser.parse_args()

    logging.basicConfig(format='[AUTOCONNECT] %(asctime)s | %(levelname)s | %(message)s', 
        level=logging.DEBUG if args.verbose else logging.INFO)

    config = configparser.ConfigParser(allow_no_value=True)
    with open(args.config, 'r') as f: # do it like this to detect non existand files
        config.read_file(f)

    scanner = BleakScanner(detection_callback)
    locked_devices = [] # list of uuids

    loop = asyncio.new_event_loop()
    loop.create_task(start_scan())
    loop.run_forever()
