# BLE Serial
A tool to connect Bluetooth 4.0+ Low Energy to UART modules and normal PCs/laptops/RaspberryPi. 
It fulfills the same purpose as `rfcomm bind` for the old Bluetooth 2.0, creating a virtual serial port in `/dev/pts/x`, which makes it usable with any terminal or application.

### Installation
The software is written completely in Python and packaged as module, so it can be easily installed with pip:
```
pip install ble-serial
pip install git+https://github.com/edwios/bluepy.git@10f1cee90afb416f139949b86b491e4cfa98c886
```
If you are wondering why the second command is required: It depends on the bluepy library, but unfortunately there are [bugs](https://github.com/IanHarvey/bluepy/issues/253) in the original version and there was no development since a year, so it is important to specifically install this fork with a few fixes.

Now you should have 2 new scripts: `ble-scan` and the main `ble-serial`.

Note: To be able to run scripts without using `sudo` or root, you must grant the `bluepy-helper` binary additional [capabilities/permissions](https://github.com/IanHarvey/bluepy/issues/313#issuecomment-428324639). Follow the steps outlined below:

Find bluepy-helper (typically ~/.local/lib/python3.6/site-packages/bluepy/bluepy-helper).

Give it permissions so you don't have to run scripts with sudo:
```sh
sudo setcap 'cap_net_raw,cap_net_admin+eip' bluepy-helper`
```

### Finding devices
First make sure the bluetooth adapter is enabled, for example with `bluetoothctl power on`, then the scan function can be used (note: root is required for this step):
```
# ble-scan
```
```
Discovered device: 20:91:48:4c:4c:54 -> UT61E - JK
...
Found 2 devices!

Device 20:91:48:4c:4c:54 (public), RSSI=-58 dB
    01: Flags = 06
    ff: Manufacturer = 484d2091484c4c54
    16: 16b Service Data = 00b000000000
    02: Incomplete 16b Services = 0000ffe0-0000-1000-8000-00805f9b34fb
    09: Complete Local Name = UT61E -  JK
    0a: Tx Power = 00

Device ...
```
The output is a list of the recognized nearby devices. After the MAC address it prints out the device name, if it can be resolved.

If there are devices not found it might help to increase the scan time. All discoverable devices must actively send advertisements, to save power the intervall of this can be quite slow, so try for example 30 seconds then.
```
optional arguments:
  -h, --help            show this help message and exit
  -t SEC, --scan-time SEC
                        Duration of the scan in seconds (default: 5.0)
  -d, --deep-scan       Try to connect to the devices and read out the service/characteristic UUIDs (default: False)
```
On Bluetooth 2.0 there was a "serial port profile", with 4.0 BLE there is unfortunately no standardized mode anymore, every chip manufacturer chooses their own ID to implement the features there. 
```py
'0000ff02-0000-1000-8000-00805f9b34fb', # LithiumBatteryPCB adapter
'0000ffe1-0000-1000-8000-00805f9b34fb', # TI CC245x (HM-10, HM-11)
```
Some usual IDs are included in ble-serial, these will be tried automatically if nothing is specified.
You might skip this part and start directly with the connection.

To find the correct ID otherwise i added a deep scan option, it will go through the devices and show all provided interfaces. This scan can take long, especially if there are many devices in the area, so only use it if you want to find the right write characteristic ID.
```
# ble-scan -d
```
```
  Device ...
  ...
  Service: 00001800-0000-1000-8000-00805f9b34fb
    Characteristic: 00002a00-0000-1000-8000-00805f9b34fb READ 
    Characteristic: 00002a01-0000-1000-8000-00805f9b34fb READ 
    Characteristic: 00002a02-0000-1000-8000-00805f9b34fb READ WRITE 
    Characteristic: 00002a03-0000-1000-8000-00805f9b34fb READ WRITE 
    Characteristic: 00002a04-0000-1000-8000-00805f9b34fb READ 
  Service: 00001801-0000-1000-8000-00805f9b34fb
    Characteristic: 00002a05-0000-1000-8000-00805f9b34fb INDICATE 
  Service: 0000ffe0-0000-1000-8000-00805f9b34fb
    Characteristic: 0000ffe1-0000-1000-8000-00805f9b34fb READ WRITE NO RESPONSE NOTIFY 
```
Now in addition to the previous output there are all characteristics listed, grouped into services. The characteristics in the first service starting with `00002a` are not interesting in this case, because they are standard values (for example the device name), if you want to know more look at [this list](https://gist.github.com/sam016/4abe921b5a9ee27f67b3686910293026#file-allgattcharacteristics-java-L57).

After the (U)ID the permissions are listed. We are searching for a characteristic that allows writing = sending to the device, the only candidate in here is `0000ffe1-0000-1000-8000-00805f9b34fb` (spoiler: a HM-11 module again).



### Connecting a device
The `ble-serial` tool itself has a few more options:
```
  -h, --help            show this help message and exit
  -v                    Increase verbosity (logs all data going through)
  -d DEVICE, --dev DEVICE
                        BLE device address to connect (hex format, can be seperated by colons)
  -w WRITE_UUID, --write-uuid WRITE_UUID
                        The GATT chracteristic to write the serial data, you might use "scan.py -d" to find it out
  -l FILENAME, --log FILENAME
                        Enable optional logging of all bluetooth traffic to file
  -p PORT, --port PORT  Symlink to virtual serial port (default = /tmp/ttyBLE)
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

Now it is possible to use any serial monitor program, just connect to that port, baud rate etc. does not matter, it will work with any value (ignored it is only virtual).
The software acts as transparent bridge, everything that is sent to that virtual port gets transmitted to the BLE module and comes out of the TX pin there. Same in the other direction, everything that the BLE module receives on the RX pin gets transmitted to the PC and shows up in the virtual serial port. This makes also possible to add ble module to create a wireless serial connection with existing hard/software.

As mentioned before, the start might fail because the ID is not in the list, then you have can manually specify the correct characteristic ID like this:
```
$ ble-serial -d 20:91:48:4c:4c:54 -w 0000ffe1-0000-1000-8000-00805f9b34fb
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
* Chromium 73+ based applications, including NW.js/electron desktop apps, for example current Betaflight/INAV Configurator: Connection to the virtual serial port (pty) fails. Read more in [issue #6](https://github.com/Jakeler/ble-serial/issues/6).
