import platform

if platform.system() == 'Linux':
    from ble_serial.ports.linux_pty import UART as platform_uart
elif platform.system() == 'Windows':
    from ble_serial.ports.windows_com0com import COM as platform_uart
else:
    raise Exception('Platform not supported!')