import asyncio
import logging
from ble_serial.bluetooth.ble_client import BLE_client

def receive_callback(value: bytes):
    print("Received:", value)

async def hello_sender(ble: BLE_client):
    while True:
        await asyncio.sleep(3.0)
        print("Sending...")
        ble.queue_send(b"Hello world\n")

async def main():
    # None uses default/autodetection, insert values if needed
    ADAPTER = "hci0"
    SERVICE_UUID = None
    WRITE_UUID = None
    READ_UUID = None
    DEVICE = "20:91:48:4C:4C:54"
    WRITE_WITH_RESPONSE = False

    ble = BLE_client(ADAPTER, 'ID')
    ble.set_receiver(receive_callback)

    try:
        await ble.connect(DEVICE, "public", SERVICE_UUID, 10.0)
        await ble.setup_chars(WRITE_UUID, READ_UUID, "rw", WRITE_WITH_RESPONSE)

        await asyncio.gather(ble.send_loop(), hello_sender(ble))
    finally:
        await ble.disconnect()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())