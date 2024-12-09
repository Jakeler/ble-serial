import asyncio
import logging
from ble_serial.bluetooth.ble_server import BLE_server

def receive_callback(value: bytes):
    print("Received:", value)

async def hello_sender(ble: BLE_server):
    while True:
        await asyncio.sleep(3.0)
        print("Sending...")
        ble.queue_send(b"Hello world\n")

async def main():
    # At least service uuid requiered here, Nordic UART service for example
    ADAPTER = "hci0"
    SERVICE_UUID = '6E400001-B5A3-F393-E0A9-E50E24DCCA9E'
    WRITE_UUID = None
    READ_UUID = None
    WRITE_WITH_RESPONSE = False

    ble = BLE_server(ADAPTER, 'ExampleServer')
    ble.set_receiver(receive_callback)

    try:
        await ble.setup_chars(SERVICE_UUID, WRITE_UUID, READ_UUID, 'rw', WRITE_WITH_RESPONSE)
        await ble.start(0) # timeout does not matter

        await asyncio.gather(ble.send_loop(), ble.check_loop(), hello_sender(ble))
    finally:
        ble.stop_loop()
        await ble.disconnect()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())