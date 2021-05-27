"""Bluetooth LE automated connections:
Uses bleak to check if devices exist, implementation should be cross platform. If a known device is found
then it should automatically start the specified tool (for example ble-serial) to connect with it.
"""

import asyncio
from bleak import BleakScanner

from pprint import pprint
from datetime import datetime
import signal


def detection_callback(device, advertisement_data):
    print(device.address, "RSSI:", device.rssi, advertisement_data)

async def main():
    scanner = BleakScanner()
    scanner.register_detection_callback(detection_callback)
    await scanner.start()

    def stop_loop(signal, stackframe):
        print('Stopping scan!')
        loop.create_task(scanner.stop())
        loop.stop()
    signal.signal(signal.SIGINT, stop_loop)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
