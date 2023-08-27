# BLE Serial
A tool to connect Bluetooth 4.0+ Low Energy to UART modules and normal PCs/laptops/RaspberryPi.

It fulfills the same purpose as `rfcomm bind` for the old Bluetooth 2.0, creating a virtual serial port in `/dev/pts/x`, which makes it usable with any terminal or application.

On Windows it provides a `COM` port, similar to the Microsoft "Standard Serial over Bluetooth" (a driver which exists since Windows XP and unsurprisingly also does not support BLE standards).

## Installation
### Standard (via [Python Package Index](https://pypi.org/project/ble-serial/))
The software is written completely in Python and packaged as module, so it can be easily installed with pip:
```console
$ pip install ble-serial
```

Now you should have 2 new scripts: `ble-scan` and the main `ble-serial`.

On Linux/Mac you are ready now and can directly jump to the usage section!
For Windows follow the [additional steps below](#additional-steps-for-windows).

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
Windows does not have a builtin feature to create virtual serial ports (like Linux does), so it is required to install a additional driver. 
I decided to use the open source `com0com` Null-modem emulator, downloaded from [here](https://sourceforge.net/projects/signed-drivers/files/com0com/v3.0/) as signed version. This is required because unsigned drivers can not be installed anymore.

**Note: on Windows 10+ you still have to disable secure boot for it to work.** Otherwise you might get a `Unexpected Error: SerialException` when starting ble-serial.

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
> ble-com-setup.exe
OK

[New Window]
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

On macOS it displays a system specific device ID instead of a MAC address:
```
55AEB150-5AF1-4318-A02E-19A46223F572 (RSSI=-70): nRF52 Accelerometer
```
It can be used simply in place of the MAC to specify a device to connect in the following section.

If there are no devices found it might help to increase the scan time. All discoverable devices must actively send advertisements, the interval of this can be quite long to save power, try for example 30 seconds in this case.
```console
$ ble-scan -h
usage: ble-scan [-h] [-t SEC] [-d ADDR]

Scanner for BLE devices and service/characteristics.

options:
  -h, --help            show this help message and exit
  -t SEC, --scan-time SEC
                        Duration of the scan in seconds (default: 5.0)
  -i ADAPTER, --interface ADAPTER
                        BLE host adapter number to use (default: hci0)
  -d ADDR, --deep-scan ADDR
                        Try to connect to device and read out service/characteristic UUIDs (default: None)
  -s SERVICE_UUID, --service-uuid SERVICE_UUID
                        The service used for scanning of potential devices (default: None)
  -v, --verbose         Print all infos from advertisement data (default: False)
```

On Bluetooth 2.0 there was a "serial port profile", with 4.0 - 5.2 (BLE) there is unfortunately no standardized mode anymore, every chip manufacturer chooses their own UUIDs to implement the features. 
```py
'0000ff01-0000-1000-8000-00805f9b34fb', # LithiumBatteryPCB adapter: read/notify
'0000ff02-0000-1000-8000-00805f9b34fb', # LithiumBatteryPCB adapter: write
'0000ffe1-0000-1000-8000-00805f9b34fb', # TI CC245x (HM-10, HM-11)
```
Some usual read/write UUIDs are included in ble-serial, these will be tried automatically if nothing is specified.
You might skip this part and start directly with the connection.

Otherwise to find the correct UUID, use the deep scan option. It expects a device MAC/ID, connects to it and reads out all services/characteristic/descriptors:
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
Now the interesting parts are the characteristics, grouped into services. The ones belows the first service starting with `00002` are not relevant in this case, because they are standard values (for example the device name), if you want to know more look at [this list](https://gist.github.com/sam016/4abe921b5a9ee27f67b3686910293026#file-allgattcharacteristics-java-L57).

After the UUID, handle and type the permissions are listed in []. We are searching for a characteristic that allows writing = sending to the device, the only candidate in here is `0000ffe1-0000-1000-8000-00805f9b34fb` (spoiler: a HM-11 module again).
Same procedure with the read characteristic, here you have to actually look for `notify` or `indicate`, that is how the receiving side is informed about new data in BLE.
This module handles both directions through the same characteristic.

Some other chips split it up, for example (this time on macOS with device ID):
```console
$ ble-scan -d 55AEB150-5AF1-4318-A02E-19A46223F572
Started deep scan of 55AEB150-5AF1-4318-A02E-19A46223F572

SERVICE 00000001-af0e-4c28-95a4-4509fd91e0bb (Handle: 10): SDP
     CHARACTERISTIC 00000006-af0e-4c28-95a4-4509fd91e0bb (Handle: 11): Unknown ['read', 'notify']
         DESCRIPTOR 00002902-0000-1000-8000-00805f9b34fb (Handle: 13): Client Characteristic Configuration
     CHARACTERISTIC 00000005-af0e-4c28-95a4-4509fd91e0bb (Handle: 14): TCS-BIN ['write-without-response', 'notify']
         DESCRIPTOR 00002902-0000-1000-8000-00805f9b34fb (Handle: 16): Client Characteristic Configuration

Completed deep scan of 55AEB150-5AF1-4318-A02E-19A46223F572
```
As you can see, here the read/notify UUID is `00000006-af0e-4c28-95a4-4509fd91e0b` and write UUID `00000005-af0e-4c28-95a4-4509fd91e0bb`.

### Connecting a device
The `ble-serial` tool itself has a few more options:
```console
$ ble_serial -h
usage: __main__.py [-h] [-v] [-t SEC] [-i ADAPTER] [-m MTU] [-d DEVICE] [-a {public,random}] [-s SERVICE_UUID] [-w WRITE_UUID] [-r READ_UUID] [--permit {ro,rw,wo}] [-l FILENAME] [-b] [-p PORT] [--expose-tcp-host TCP_HOST] [--expose-tcp-port TCP_PORT]

Create virtual serial ports from BLE devices.

options:
  -h, --help            show this help message and exit
  -v, --verbose         Increase verbosity, can be specified multiple times for connection/DBus debugging (default: 0)

connection parameters:
  -t SEC, --timeout SEC
                        BLE connect/discover timeout in seconds (default: 5.0)
  -i ADAPTER, --interface ADAPTER
                        BLE host adapter number to use (default: hci0)
  -m MTU, --mtu MTU     Max. bluetooth packet data size in bytes used for sending (default: 20)

device parameters:
  -d DEVICE, --dev DEVICE
                        BLE device address to connect (hex format, can be separated by colons) (default: None)
  -a {public,random}, --address-type {public,random}
                        BLE address type, only relevant on Windows, ignored otherwise (default: public)
  -s SERVICE_UUID, --service-uuid SERVICE_UUID
                        The service used for scanning of potential devices (default: None)
  -w WRITE_UUID, --write-uuid WRITE_UUID
                        The GATT characteristic to write the serial data, you might use "ble-scan -d" to find it out (default: None)
  -r READ_UUID, --read-uuid READ_UUID
                        The GATT characteristic to subscribe to notifications to read the serial data (default: None)
  --permit {ro,rw,wo}   Restrict transfer direction on bluetooth: read only (ro), read+write (rw), write only (wo) (default: rw)
```

In any case it needs to know which device to connect, the simple and most reliable way to specify this is by device address/id:
```console
$ ble-serial -d 20:91:48:4c:4c:54
20:38:31.271 | INFO | linux_pty.py: Port endpoint created on /tmp/ttyBLE -> /dev/pts/5
20:38:31.271 | INFO | ble_interface.py: Receiver set up
20:38:31.485 | INFO | ble_interface.py: Trying to connect with 20:91:48:4C:4C:54: UT61E -  JK
20:38:32.844 | INFO | ble_interface.py: Device 20:91:48:4C:4C:54 connected
20:38:32.844 | INFO | ble_interface.py: Found write characteristic 0000ffe1-0000-1000-8000-00805f9b34fb (H. 17)
20:38:32.844 | INFO | ble_interface.py: Found notify characteristic 0000ffe1-0000-1000-8000-00805f9b34fb (H. 17)
20:38:33.128 | INFO | main.py: Running main loop!

```
This log shows a successful start on Linux, the virtual serial port was opened on `/dev/pts/8`, the number at the end changes, depending on how many pseudo terminals are already open on the system. It uses the same mechanism on macOS, just the path is slightly different, in the format `/dev/ttys000`.
In addition it automatically creates a symlink to `/tmp/ttyBLE`, so you can easily access it always on the same file, the default can be changed with:
```
serial port parameters:
  -p PORT, --port PORT  Symlink to virtual serial port (default: /tmp/ttyBLE)
```

On Windows it uses the port pair created in the setup described above, this does not dynamically change and endpoint is always `COM9` if you use the default script.

Now it is possible to use any serial monitor program, just connect to that port, baud rate etc. does not matter, it will work with any value (settings are ignored, because it is only virtual).
The software acts as transparent bridge, everything that is sent to that virtual port gets transmitted to the BLE module and comes out of the TX pin there. Same in the other direction, everything that the BLE module receives on the RX pin gets transmitted to the PC and shows up in the virtual serial port. This makes it also possible to add ble module to create a wireless serial connection with existing hard/software.

Another way to find a device is by service uuid:
```console
$ ble-serial -s 0000ffe0-0000-1000-8000-00805f9b34fb
20:35:41.964 | INFO | linux_pty.py: Port endpoint created on /tmp/ttyBLE -> /dev/pts/5
20:35:41.964 | INFO | ble_interface.py: Receiver set up
20:35:41.964 | WARNING | ble_interface.py: Picking first device with matching service, consider passing a specific device address, especially if there could be multiple devices
20:35:42.308 | INFO | ble_interface.py: Trying to connect with 20:91:48:4C:4C:54: UT61E -  JK
20:35:43.020 | INFO | ble_interface.py: Device 20:91:48:4C:4C:54 connected
...
```
This has the advantage that you can replace the device/chip without changing anything in the host script, it will automatically pick the first device that provides the service. It is also possible to add both the service and address, then it will only connect if both match.
On early versions of macOS 12 (Monterey) it is always required to filter with the service uuid, otherwise scanning/connecting won't work.

As mentioned before, the start might fail because the characteristic UUIDs are not in the list, then you can manually specify the correct write UUID like this:
```
$ ble-serial -d 20:91:48:4c:4c:54 -w 0000ffe1-0000-1000-8000-00805f9b34fb
```

Same for reading with `-r`/`--read-uuid`, for example:
```
$ ble-serial -d 20:91:48:4c:4c:54 -r 0000ffe1-0000-1000-8000-00805f9b34fb
```

Per default it always tries to setup reading and writing and searches for both characteristics. If none of your characteristics are in the builtin list then you have to specify both `-w` and `-r`. 

Otherwise if your device has only a read/notify characteristic or you want to intentionally prevent writing then you can use `--permit`:
```
$ ble-serial -d 20:91:48:4c:4c:54 -r 0000ffe1-0000-1000-8000-00805f9b34fb --permit ro
```
Here `-r` is enough for `ro` = read only. 
This works also the other way around with `wo` = write only.

### Log to file
There is an option to log all traffic on the link to a text file:
```
logging options:
  -l FILENAME, --log FILENAME
                        Enable optional logging of all bluetooth traffic to file (default: None)
  -b, --binary          Log data as raw binary, disable transformation to hex. Works only in combination with -l (default: False)
```

```console
$ ble-serial -d 20:91:48:4c:4c:54 -l demo.txt
...
$ cat demo.txt
2019-12-09 21:15:53.282805 <- BLE-OUT: 48 65 6c 6c 6f 20 77 6f 72 6c 64
2019-12-09 21:15:53.491681 -> BLE-IN: b0 b0 b0 b0 b0 b0 3b b0 b0 b0 ba b0 0d 8a
2019-12-09 21:15:53.999795 -> BLE-IN: b0 b0 b0 b0 b0 b0 3b b0 b0 b0 ba b0 0d 8a
```
Per default it is transformed to hex bytes, use `-b`/`--binary` to log raw data, useful if your input is already ASCII etc.

## Advanced Usage
### TCP socket server
Instead of the serial port emulation there is a also builtin raw tcp server since version 2.7:
```
network options:
  --expose-tcp-host TCP_HOST
                        Network interface for the server listen on (default: 127.0.0.1)
  --expose-tcp-port TCP_PORT
                        Port to listen on, disables local serial port and enables TCP server if specified (default: None)
```
This is only activated if TCP_PORT is set. Also it removes the dependency to com0com or other drivers.

The server is listening on localhost per default, therefore only reachable from apps running on the same machine. Other interfaces or `0.0.0.0` for all interfaces can be specified with TCP_HOST.
Security is to consider though, this is plain TCP without encryption or authentication. Only recommended on a separate local network, otherwise stay with the default/localhost.

Note: this is limited to one concurrent connection, it will reject all connection attempts if there is already a client connected and emit a warning, example:
```console
$ ble-serial -d 20:91:48:4C:4C:54 --expose-tcp-port 4002 -v
[...]
19:30:11.650 | INFO | main.py: Running main loop!
19:30:11.650 | INFO | tcp_socket.py: TCP server started
19:30:11.650 | DEBUG | tcp_socket.py: Listening on <asyncio.TransportSocket fd=8, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=6, laddr=('127.0.0.1', 4002)>
[...]
19:30:13.618 | INFO | tcp_socket.py: New TCP peer connected: ('127.0.0.1', 49104)
19:30:13.787 | DEBUG | ble_interface.py: Received notify from 0000ffe1-0000-1000-8000-00805f9b34fb (Handle: 17): Vendor specific: bytearray(b'\xb0\xb0\xb0\xb01\xb6;\xb0\xb0\xb0\xba\xb0\r\x8a')
19:30:13.787 | DEBUG | tcp_socket.py: Sending: bytearray(b'\xb0\xb0\xb0\xb01\xb6;\xb0\xb0\xb0\xba\xb0\r\x8a')
[...]
19:30:26.726 | INFO | tcp_socket.py: New TCP peer connected: ('127.0.0.1', 56172)
19:30:26.726 | WARNING | tcp_socket.py: More than one connection is not allowed, closing
```

Now there a various ways to connect to it. 
#### Linux and macOS
- Very simple option: `netcat 127.0.0.1 4002` or `telnet 127.0.0.1 4002`
- More powerful: `socat -dd tcp:localhost:4002 -`, can forward data to many modules, not only stdin/stdout.
- Custom apps are easy to make with tcp too
#### Windows
- Graphical: Putty, just put in the IP+port and select Other - Raw as connection type.
- Terminal: netcat/telnet/socat can be installed separately

### Multi device connection
It is possible to connect several devices to a host simultaneously. Limiting factor is only the bluetooth baseband layer, which uses a Active Member Address (AMA, 3 bit). From these 8 possible values address zero is always occupied by the host, so it can be connected to (up to) 7 devices at the same time.

There is no special mode, ble-serial can be just started multiple times with different parameters. Following are some tips, showing how to do this in practice.

#### Linux and macOS
Common shells (bash, zsh, fish) have a useful background job feature. Add the `-p` (port) option to make sure every instance has a unique path. Also you probably want to redirect the log output to keep it separate. Resulting command lines could look like:
```terminal
$ ble-serial -d $ADDR1 -p /tmp/ttyBLE1 2> dev1.log &
[1] 178378

$ ble-serial -d $ADDR2 -p /tmp/ttyBLE2 2> dev2.log &
[2] 178397
```
The `&`  at the end causes it to go into background mode immediately, showing the job number and PID. 
Now it is usual control, here are 2 running visible with `jobs` as expected:
```
$ jobs                                                     
[1]  - running   ble-serial -d ... -p /tmp/ttyBLE1 2> dev1.log &
[2]  + running   ble-serial -d ... -p /tmp/ttyBLE2 2> dev2.log &
```
Get them back to foreground with `fg` or view logs live with `tail -f dev1.log` etc.
Of course you can also put everything into a shell script. 
For stopping multiple instances you can send signals with `kill -s SIGINT $PID`, this will bring ble-serial to graceful shutdown as well, same as ctrl-c.

#### Windows
More com0com port pairs need to be created manually: go to `Program Files (x86)/com0com` and either use command line `setupc.exe` `install` or the graphical `setupg.exe` 'Add pair' button. The PortNames can be chosen arbitrarily at least for the ble-serial side, but I would recommend to use something between COM1-COM9 for the external side, because I noticed many other applications are incompatible with different naming schemes. So use for example BLE2 <> COM8, BLE3 <> COM7 and so on.

Default cmd has no real background job feature, instead multiple cmd windows or Windows Terminal with tabs can do the trick.
Make sure to specify the right port for every additional instance, example:
```
[Window/Tab 1]
> ble-serial -d ... -p BLE
```
```
[Window/Tab 2]
> ble-serial -d ... -p BLE2
```
```
[Window/Tab 3]
> ble-serial -d ... -p BLE3
```

### Automated connections
The repo [`helper/`](https://github.com/Jakeler/ble-serial/tree/master/helper) directory contains a `ble-autoconnect.py` script:
```console
$ python helper/ble-autoconnect.py -h
usage: ble-autoconnect.py [-h] [-c CONFIG] [-v]

Service to automatically connect with devices that get available.

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Path to a INI file with device configs (default: autoconnect.ini)
  -v, --verbose         Increase log level from info to debug (default: False)

```
This continuously scans for devices and compares them with the configuration, it then automatically starts up `ble-serial` (or other tools) if a known device is detected.
This should bring similar convenience like USB adapters, just turn the BLE device on and
the serial port shows up on the PC. See the example `autoconnect.ini` for configuration.

On Linux you can also use the included systemd (user) service to auto start this on boot.

### Usage as library
ble-serial is primarily designed for command line usage. Nonetheless it is possible to import modules of it into another python application. See the
[`examples/`](https://github.com/Jakeler/ble-serial/tree/master/examples) dir for how to use the ble parts directly.

## Troubleshooting
First you can use `-v` to increase the log verbosity to DEBUG:
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

If this is not enough use the double verbose `-vv` flag. It activates debug logging also for the underlying [bleak](https://github.com/hbldh/bleak) module and shows interactions with the bluetooth stack more detailed.
Check out the [issue tracker](https://github.com/hbldh/bleak/issues) there too, it is often helpful for problems not directly caused by ble-serial. 

## Known limitations
* Chromium 73+ based applications, including NW.js/electron desktop apps. Connection to the virtual serial port (pty) fails. This is because of explicit whitelisting in chromium. 
TCP might be an alternative (see above), for example in Betaflight Configurator with Manual selection and `tcp://IP:PORT` url as port.

* Certain baud/chipset/firmware configurations can have significant packet loss, see my [benchmark blog post](https://blog.ja-ke.tech/2021/04/22/ble-serial-2.html#performance) with the HM-10 module. Consider other protocols if the application requires constant high bandwidth, short bursts of data are usually fine though.

## Closing remarks
If you encounter unexpected problems, please use the [issue tracker](https://github.com/Jakeler/ble-serial/issues). For general questions there is also the discussions tab.
As always, I hope it was helpful, if you like it then I would appreciate if you could star it on [GitHub](https://github.com/Jakeler/ble-serial). 

