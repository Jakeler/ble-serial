"""Bluetooth LE automated connections:
This script listens on the system DBus for events of BlueZ scan. 
So far only a more low level proof of concept that just logs detected devices. 
Use the bleak based `ble-autoconnect.py` to actually connect and start ble-serial.
"""

import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

from pprint import pprint
from datetime import datetime
import signal


def print_dev(dev: dict[str, dict]):
    state = 'CONNECTED' if dev['Connected'] else 'NOT connected'
    print(f"{dev['Address']} = {dev['Alias']} (RSSI: {dev['RSSI']}) {state}")


def dbus_handler(obj_path, props, member):
    print(datetime.now().strftime('%H:%M:%S.%f'))

    if member == 'InterfacesAdded':
        print('ADDED', obj_path)

        dev = props.get('org.bluez.Device1', None)
        if dev:
            print_dev(dev)
    elif member == 'InterfacesRemoved':
        print('REMOVED', obj_path)
        pprint(props)
    else:
        print('UNKNOWN')
        return
    print()


# based on https://github.com/bluez/bluez/blob/5.58/test/test-device
def get_current_devices(obj_manager: dbus.Interface):
    objects = obj_manager.GetManagedObjects()

    # pprint(objects)
    for path, interfaces in objects.items():
        if "org.bluez.Device1" not in interfaces:
            continue
        props = interfaces["org.bluez.Device1"]
        print_dev(props)


def stop_loop(signal, stackframe):
    loop.quit()

if __name__ == "__main__":
    DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    obj = bus.get_object("org.bluez", '/')
    obj_manager = dbus.Interface(obj, "org.freedesktop.DBus.ObjectManager")

    obj_manager.connect_to_signal(
            None, # signal name / member
            # signal_name='InterfacesAdded',
            dbus_handler,
            # bus_name='org.bluez',
            # dbus_interface='org.freedesktop.DBus.ObjectManager',
            member_keyword='member',
        )

    get_current_devices(obj_manager)

    loop = GLib.MainLoop()
    signal.signal(signal.SIGINT, stop_loop)
    signal.signal(signal.SIGTERM, stop_loop)
    loop.run()