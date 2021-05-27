# BLE Serial
A tool to connect Bluetooth 4.0+ Low Energy to UART modules and normal PCs/laptops/RaspberryPi.

It fulfills the same purpose as `rfcomm bind` for the old Bluetooth 2.0, creating a virtual serial port in `/dev/pts/x`, which makes it usable with any terminal or application.

On Windows it provides a `COM` port, similar to the Microsoft "Standard Serial over Bluetooth" (a driver which exists since Windows XP and unsurprisingly also does not support BLE standards).

## Installation
### Standard (via Python Package Index)
The software is written completely in Python and packaged as module, so it can be easily installed with pip:
```console
$ pip install ble-serial
```

Now you should have 2 new scripts: `ble-scan` and the main `ble-serial`.

On Linux you are ready now and can directly jump to the usage section!

### From source (for developers)
You can clone the repository with:
```console
$ git clone https://github.com/Jakeler/ble-serial.git
```

Then switch branches, make changes etc... 
Make sure the dependencies are installed, I recommend to use a virtualenv like this:
```console
$ python -m venv ble-venv
$ source ble-venv/bin/activate
$ pip install -r requirements.txt
```

The package can be either started directly with `-m`:
```console
$ python -m ble_serial ARGUMENTS # Main tool = ble-serial
$ python -m ble_serial.scan # BLE scan = ble-scan
$ python -m ble_serial.setup_com0com # Windows only setup = ble-com-setup
```

Or installed with `pip` from the current directory:
```console
$ pip install .
```
and started as usual.

### Additional steps for Windows
Windows does not have a builtin feature to create virtual serial ports (like Linux does), so it is required to install a additional driver. I decided to use the open source `com0com` Null-modem emulator, downloaded from [here](https://sourceforge.net/projects/signed-drivers/files/com0com/v3.0/) as signed version. This is required because unsigned drivers can not be installed anymore. Note that on latest Windows 10 you likely still have to disable secure boot for it to work.

ble-serial includes the `ble-com-setup` script to make the `com0com` configuration easier:
```console
> ble-com-setup.exe -h
usage: ble-com-setup [-h] [--install-path INSTALL_PATH]

Setup required COM port pair

optional arguments:
  -h, --help            show this help message and exit
  --install-path INSTALL_PATH
                        Installation directory of the null modem emulator (default: C:/Program Files (x86)/com0com/)
```

It will request administrator privileges (if it does not already have it) and setup the port in another CMD window:
```
Changing into C:/Program Files (x86)/com0com/

> Checking port list for BLE
       CNCA0 PortName=-
       CNCB0 PortName=-

BLE port does not exist

> Checking port list for COM9
       CNCA0 PortName=-
       CNCB0 PortName=-

> Trying to create port pair
       CNCA1 PortName=COM9
       CNCB1 PortName=BLE
ComDB: COM9 - logged as "in use"

Setup done!

Hit any key to close
```
As you can see it created the `BLE`<->`COM9` pair. ble-serial will internally connect to `BLE`, users can then send/receive the data on `COM9`.

Otherwise there exist multiple proprietary serial port emulators, these should work too. Just manually create a pair that includes a port named `BLE`.

## Usage
### Finding devices
First make sure the bluetooth adapter is enabled, for example with `bluetoothctl power on`, then the scan function can be used:
```console
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
'0000ff01-0000-1000-8000-00805f9b34fb', # LithiumBatteryPCB adapter: read/notify
'0000ff02-0000-1000-8000-00805f9b34fb', # LithiumBatteryPCB adapter: write
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
Now the interesting parts are the characteristics, grouped into services. The ones belows the first service starting with `00002` are not interesting in this case, because they are standard values (for example the device name), if you want to know more look at [this list](https://gist.github.com/sam016/4abe921b5a9ee27f67b3686910293026#file-allgattcharacteristics-java-L57).

After the ID, handle and type the permissions are listed in []. We are searching for a characteristic that allows writing = sending to the device, the only candidate in here is `0000ffe1-0000-1000-8000-00805f9b34fb` (spoiler: a HM-11 module again). 
Same procedure with the read characteristic, this modules handles read and write through the same characteristic, but some other chips split it up.


### Connecting a device
The `ble-serial` tool itself has a few more options:
```console
$ ble_serial -h
usage: __main__.py [-h] [-v] -d DEVICE [-t {public,random}] [-i ADAPTER] [-m MTU] [-w WRITE_UUID] [-l FILENAME] [-b]
                   [-p PORT] [-r READ_UUID]

Create virtual serial ports from BLE devices.

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Increase verbosity to log all data going through (default: False)
  -p PORT, --port PORT  Symlink to virtual serial port (default: /tmp/ttyBLE)
  -d DEVICE, --dev DEVICE
                        BLE device address to connect (hex format, can be separated by colons) (default: None)
  -t SEC, --timeout SEC
                        BLE connect/discover timeout in seconds (default: 5.0)
  -a {public,random}, --address-type {public,random}
                        BLE address type, either public or random (default: public)
  -i ADAPTER, --interface ADAPTER
                        BLE host adapter number to use (default: hci0)
  -m MTU, --mtu MTU     Max. bluetooth packet data size in bytes used for sending (default: 20)
  -w WRITE_UUID, --write-uuid WRITE_UUID
                        The GATT characteristic to write the serial data, you might use "ble-scan -d" to find it out (default: None)
  -r READ_UUID, --read-uuid READ_UUID
                        The GATT characteristic to subscribe to notifications to read the serial data (default: None)
  -l FILENAME, --log FILENAME
                        Enable optional logging of all bluetooth traffic to file (default: None)
  -b, --binary          Log data as raw binary, disable transformation to hex. Works only in combination with -l (default: False)

```
Only the device address is always required:
```console
$ ble-serial -d 20:91:48:4c:4c:54
18:36:09.255 | INFO | linux_pty.py: Slave created on /tmp/ttyBLE -> /dev/pts/7
18:36:09.255 | INFO | ble_interface.py: Receiver set up
18:36:09.258 | INFO | ble_interface.py: Trying to connect with 20:91:48:4C:4C:54
18:36:12.291 | INFO | ble_interface.py: Device 20:91:48:4C:4C:54 connected
18:36:12.637 | INFO | main.py: Running main loop!
```
This log shows a successful start, the virtual serial port was opened on `/dev/pts/8`, the number at the end changes, depending on how many pseudo terminals are already open on the system. 
In addition it automatically creates a symlink to `/tmp/ttyBLE`, so you can easily access it always on the same file, the default can be changed with the `-p`/`--port` option.

Now it is possible to use any serial monitor program, just connect to that port, baud rate etc. does not matter, it will work with any value (settings are ignored, because it is only virtual).
The software acts as transparent bridge, everything that is sent to that virtual port gets transmitted to the BLE module and comes out of the TX pin there. Same in the other direction, everything that the BLE module receives on the RX pin gets transmitted to the PC and shows up in the virtual serial port. This makes it also possible to add ble module to create a wireless serial connection with existing hard/software.

As mentioned before, the start might fail because the ID is not in the list, then you can manually specify the correct write characteristic ID like this:
```
$ ble-serial -d 20:91:48:4c:4c:54 -w 0000ffe1-0000-1000-8000-00805f9b34fb
```

Same for reading with `-r`/`--read-uuid`, for example:
```
$ ble-serial -d 20:91:48:4c:4c:54 -r 0000ffe1-0000-1000-8000-00805f9b34fb
```

Also there is an option to log all traffic on the link to a text file:
```console
$ ble-serial -d 20:91:48:4c:4c:54 -l demo.txt
...
$ cat demo.txt
2019-12-09 21:15:53.282805 <- BLE-OUT: 48 65 6c 6c 6f 20 77 6f 72 6c 64
2019-12-09 21:15:53.491681 -> BLE-IN: b0 b0 b0 b0 b0 b0 3b b0 b0 b0 ba b0 0d 8a
2019-12-09 21:15:53.999795 -> BLE-IN: b0 b0 b0 b0 b0 b0 3b b0 b0 b0 ba b0 0d 8a
```
Per default it is transformed to hex bytes, use `-b`/`--binary` to log raw data.

You can use `-v` to increase the log verbosity to DEBUG:
```console
18:31:25.136 | DEBUG | ble_interface.py: Received notify from 17: bytearray(b'\xb0\xb0\xb0\xb0\xb0\xb0;\xb0\xb0\xb0\xba\xb0\r\x8a')
18:31:25.136 | DEBUG | linux_pty.py: Write: bytearray(b'\xb0\xb0\xb0\xb0\xb0\xb0;\xb0\xb0\xb0\xba\xb0\r\x8a')

18:31:25.373 | DEBUG | linux_pty.py: Read: b'hello world'
18:31:25.373 | DEBUG | ble_interface.py: Sending b'hello world'
```
This will log all traffic going through. Note that everything shows up two times, because it goes through the ble module and then into the serial port and vice versa.
It also helps with figuring out how characteristics are selected:
```console
14:32:47.589 | DEBUG | ble_interface.py: No write uuid specified, trying builtin list
14:32:47.589 | DEBUG | ble_interface.py: Characteristic candidates for write: 
        0000ffe1-0000-1000-8000-00805f9b34fb (Handle: 17): Vendor specific ['read', 'write-without-response', 'notify']
14:32:47.589 | INFO | ble_interface.py: Found write characteristic 0000ffe1-0000-1000-8000-00805f9b34fb (H. 17)
14:32:47.589 | DEBUG | ble_interface.py: No notify uuid specified, trying builtin list
14:32:47.589 | DEBUG | ble_interface.py: Characteristic candidates for notify: 
        0000ffe1-0000-1000-8000-00805f9b34fb (Handle: 17): Vendor specific ['read', 'write-without-response', 'notify']
14:32:47.589 | INFO | ble_interface.py: Found notify characteristic 0000ffe1-0000-1000-8000-00805f9b34fb (H. 17)
```
Always try the verbose option if something is not working properly.

As always, I hope it was helpful. If you encounter problems, please use the issue tracker on [GitHub](https://github.com/Jakeler/ble-serial/issues).

### Known limitations
* Chromium 73+ based applications, including NW.js/electron desktop apps, for example current Betaflight/INAV Configurator: Connection to the virtual serial port (pty) fails. This is because of explicit whitelisting in chromium.
