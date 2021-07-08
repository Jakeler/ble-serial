import platform

if platform.system() in ['Linux', 'Darwin']:
    from ble_serial.ports.linux_pty import UART as platform_uart
    DEFAULT_PORT = '/tmp/ttyBLE'
    DEFAULT_PORT_MSG = 'Symlink to virtual serial port'
elif platform.system() == 'Windows':
    from ble_serial.ports.windows_com0com import COM as platform_uart
    DEFAULT_PORT = 'BLE'
    DEFAULT_PORT_MSG = 'Internal COM port to read and write bluetooth data'
else:
    raise Exception('Platform not supported!')