from serial import Serial

# AT command and responses
CMD = ('AT', 'OK')
CMD_BAUD = ('AT+BAUD{:d}', 'OK+Set:{:d}')
CMD_RESET = ('AT+RESET', 'OK+RESET')

# Interfaces
PORT_UART = '/dev/ttyUSB0'
PORT_BLE = '/tmp/ttyBLE'
BAUDS = [
    9600,
    19200,
    38400,
    57600,
    115200,
    4800,
    2400,
    1200,
    230400,
]

def set_module_baud(conn_baud: int, target_baud: int):
    with Serial(PORT_UART, BAUDS[conn_baud], timeout=.2) as ser:
        assert run_cmd(ser, CMD)
        assert run_cmd(ser, [s.format(target_baud) for s in CMD_BAUD])
        assert run_cmd(ser, CMD_RESET)

def run_cmd(ser: Serial, cmd: tuple[str, str]) -> bool:
    ser.write(cmd[0].encode())
    out = ser.read(size=32).decode()
    print(f'CMD: {cmd[0]} > {out}')
    return out == cmd[1]

set_module_baud(0, 0)
