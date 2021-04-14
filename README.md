# BLE Serial
A tool to connect Bluetooth 4.0+ Low Energy to UART modules and normal PCs/laptops/RaspberryPi. 
It fulfills the same purpose as `rfcomm bind` for the old Bluetooth 2.0, creating a virtual serial port in `/dev/pts/x`, which makes it usable with any terminal or application.

## Installation
### Standard (via Python Package Index)
The software is written completely in Python and packaged as module, so it can be easily installed with pip:
```console
pip install ble-serial
```

Now you should have 2 new scripts: `ble-scan` and the main `ble-serial`.

On Linux you ready now and can directly jump to the usage section!

### From source/local (for developers)
You can clone the repository with:
```console
git clone https://github.com/Jakeler/ble-serial.git
```

Then switch branches, make changes etc... 
The package can be started directly with `-m`:
```console
python -m ble_serial ARGUMENTS # Main tool = ble-serial
python -m ble_serial.scan # BLE scan = ble-scan
python -m ble_serial.setup_com0com # Windows only setup = ble-setup
```

Or install it with `pip` from the current directory:
```console
pip install .
```

## Usage
### Finding devices
First make sure the bluetooth adapter is enabled, for example with `bluetoothctl power on`, then the scan function can be used:
```
$ ble-scan

Started BLE scan

20:91:48:4C:4C:54 (RSSI=-56): UT61E -  JK
...

Finished BLE scan
```
The output is a list of the recognized nearby devices. After the MAC address and signal strength it prints out the device name, if it can be resolved.

If there are no devices found it might help to increase the scan time. All discoverable devices must actively send advertisements, the interval of this can be quite long  to save power, so try for example 30 seconds in this case.
```console
$ ble-scan -h
usage: ble-scan [-h] [-t SEC] [-d ADDR]

Scanner for BLE devices and service/characteristics.

optional arguments:
  -h, --help            show this help message and exit
  -t SEC, --scan-time SEC
                        Duration of the scan in seconds (default: 5.0)
  -d ADDR, --deep-scan ADDR
                        Try to connect to device and read out service/characteristic UUIDs 
                        (default: None)
```

On Bluetooth 2.0 there was a "serial port profile", with 4.0 - 5.2 (BLE) there is unfortunately no standardized mode anymore, every chip manufacturer chooses their own ID to implement the features. 
```py
'0000ff02-0000-1000-8000-00805f9b34fb', # LithiumBatteryPCB adapter
'0000ffe1-0000-1000-8000-00805f9b34fb', # TI CC245x (HM-10, HM-11)
```
Some usual IDs are included in ble-serial, these will be tried automatically if nothing is specified.
You might skip this part and start directly with the connection.

Otherwise to find the correct ID, use the deep scan option. It expects a device MAC address, connects to it and reads out all services/characteristic/descriptors:
```console
$ ble-scan -d 20:91:48:4C:4C:54
Started deep scan of 20:91:48:4C:4C:54

SERVICE 00001801-0000-1000-8000-00805f9b34fb (Handle: 12): Generic Attribute Profile
     CHARACTERISTIC 00002a05-0000-1000-8000-00805f9b34fb (Handle: 13): Service Changed ['indicate']
         DESCRIPTOR 00002902-0000-1000-8000-00805f9b34fb (Handle: 15): Client Characteristic Configuration
SERVICE 0000ffe0-0000-1000-8000-00805f9b34fb (Handle: 16): Vendor specific
     CHARACTERISTIC 0000ffe1-0000-1000-8000-00805f9b34fb (Handle: 17): Vendor specific ['read', 'write-without-response', 'notify']
         DESCRIPTOR 00002902-0000-1000-8000-00805f9b34fb (Handle: 19): Client Characteristic Configuration
         DESCRIPTOR 00002901-0000-1000-8000-00805f9b34fb (Handle: 20): Characteristic User Description

Completed deep scan of 20:91:48:4C:4C:54
```
Now the interesting parts are the characteristics, grouped into services. The ones belows the first service starting with `00002a` are not interesting in this case, because they are standard values (for example the device name), if you want to know more look at [this list](https://gist.github.com/sam016/4abe921b5a9ee27f67b3686910293026#file-allgattcharacteristics-java-L57).

After the ID, handle and type the permissions are listed in []. We are searching for a characteristic that allows writing = sending to the device, the only candidate in here is `0000ffe1-0000-1000-8000-00805f9b34fb` (spoiler: a HM-11 module again). Same procedure with the read characteristic.


### Connecting a device
The `ble-serial` tool itself has a few more options:
```
  -h, --help            show this help message and exit
  -v, --verbose         Increase verbosity to log all data going through (default: False)
  -d DEVICE, --dev DEVICE
                        BLE device address to connect (hex format, can be seperated by colons) (default: None)
  -t {public,random}, --address-type {public,random}
                        BLE address type, either public or random (default: public)
  -i ADAPTER, --interface ADAPTER
                        BLE host adapter number to use (default: 0)
  -w WRITE_UUID, --write-uuid WRITE_UUID
                        The GATT chracteristic to write the serial data, you might use "scan.py -d" to find it out (default: None)
  -l FILENAME, --log FILENAME
                        Enable optional logging of all bluetooth traffic to file (default: None)
  -b, --binary          Log data as raw binary, disable transformation to hex. Works only in combination with -l (default: False)
  -p PORT, --port PORT  Symlink to virtual serial port (default: /tmp/ttyBLE)
  -r READ_UUID, --read-uuid READ_UUID
                        The GATT characteristic to subscribe to notifications to read the serial data (default: None)

```
Only the device address is always required:
```
$ ble-serial -d 20:91:48:4c:4c:54
```
```
21:02:55.823 | INFO | virtual_serial.py: Slave created on /tmp/ttyBLE -> /dev/pts/8
21:02:56.410 | INFO | interface.py: Connected device 20:91:48:4c:4c:54
21:02:56.909 | INFO | interface.py: Receiver set up
21:02:56.909 | INFO | __main__.py: Running main loop!
```
This log shows a successful start, the virtual serial port was opened on `/dev/pts/8`, the number at the end changes, depending on how many pseudo terminals are already open on the system. In addition it creates automatically a symlink to `/tmp/ttyBLE`, so you can easily access it there always on the same file, the default can be changed with the `-p`/`--port` option.

Now it is possible to use any serial monitor program, just connect to that port, baud rate etc. does not matter, it will work with any value (settings are ignored, because it is only virtual).
The software acts as transparent bridge, everything that is sent to that virtual port gets transmitted to the BLE module and comes out of the TX pin there. Same in the other direction, everything that the BLE module receives on the RX pin gets transmitted to the PC and shows up in the virtual serial port. This makes it also possible to add ble module to create a wireless serial connection with existing hard/software.

As mentioned before, the start might fail because the ID is not in the list, then you can manually specify the correct characteristic ID like this:
```
$ ble-serial -d 20:91:48:4c:4c:54 -w 0000ffe1-0000-1000-8000-00805f9b34fb
```

Per default it does not explicitly subscribe to the read characteristic, because many modules (like HM-11) send notifications anyway. There are modules that require this though. If you don't receive any data then you have specify the uuid for reading with `-r`/`--read-uuid`, for example:
```
$ ble-serial -d 20:91:48:4c:4c:54 -r 0000ffe1-0000-1000-8000-00805f9b34fb
```

Also there is an option to log all traffic on the link to a text file:
```
$ ble-serial -d 20:91:48:4c:4c:54 -l demo.txt
cat demo.txt
```
```
2019-12-09 21:15:53.282805 <- BLE-OUT: 48 65 6c 6c 6f 20 77 6f 72 6c 64
2019-12-09 21:15:53.491681 -> BLE-IN: b0 b0 b0 b0 b0 b0 3b b0 b0 b0 ba b0 0d 8a
2019-12-09 21:15:53.999795 -> BLE-IN: b0 b0 b0 b0 b0 b0 3b b0 b0 b0 ba b0 0d 8a
```

As always, i hope it was helpful. If you encounter problems, please use the issue tracker on [GitHub](https://github.com/Jakeler/ble-serial/issues).

### Known limitations
* Higher bitrates: 9600 bit/s is well tested and works fine. 19200 and higher can cause data loss on longer transmissions.
* Chromium 73+ based applications, including NW.js/electron desktop apps, for example current Betaflight/INAV Configurator: Connection to the virtual serial port (pty) fails. This is because of explicit whitelisting in chromium.
