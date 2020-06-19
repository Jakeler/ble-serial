### BLE Serial
A tool to connect Bluetooth 4.0+ Low Energy (BLE) UART modules and normal PCs/laptops. 
It fulfills the same purpose as `rfcomm bind` for the old Bluetooth 2.0, creating a virtual serial port in `/dev/pts/x`, which makes it usable with any terminal or application.

Installation with pip: https://pypi.org/project/ble-serial/

Detailed post: https://blog.ja-ke.tech/2019/12/18/ble-serial.html

Note: To be able to run scripts without using `sudo` or root, you must grant the `bluepy-helper` binary additional capabilities/permissions. Follow the steps outlined below:

Find bluepy-helper (typically ~/.local/lib/python3.6/site-packages/bluepy/bluepy-helper or so)

Give it permissions so you don't have to run scripts with sudo:

`sudo setcap 'cap_net_raw,cap_net_admin+eip' bluepy-helper`

See the below discussion regarding this:

https://github.com/IanHarvey/bluepy/issues/313#issuecomment-428324639
