import asyncio
import logging
from ble_serial.bluetooth.ble_interface import BLE_interface

rx_buffer = b''
rx_available = asyncio.Event()

def receive_callback(value: bytes):
    print("Received:", value)
    global rx_buffer
    rx_buffer = value
    rx_available.set()

async def sendble(ble: BLE_interface, cmd):
    #while True:
    await asyncio.sleep(3.0)

    print("Sending...", cmd)
    rx_available.clear()
    ble.queue_send(cmd)

    await rx_available.wait()
    print('got response', rx_buffer)

    await asyncio.sleep(3.0)

async def commander(ble: BLE_interface):
    await sendble(ble, b'$C$')
    await sendble(ble, b'$B$')
    await ble.disconnect()

async def main():
    # None uses default/autodetection, insert values if needed
    ADAPTER = "hci0"
    SERVICE_UUID = None
    WRITE_UUID = None
    READ_UUID = None
    DEVICE = "20:91:48:4C:4C:54"

    ble = BLE_interface(ADAPTER, SERVICE_UUID)
    ble.set_receiver(receive_callback)

    await ble.connect(DEVICE, "public", 10.0)
    await ble.setup_chars(WRITE_UUID, READ_UUID, "rw")

    await asyncio.gather(ble.send_loop(), commander(ble))



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())


