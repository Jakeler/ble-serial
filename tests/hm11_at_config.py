from serial import Serial

# AT command and responses
CMD = ('AT', 'OK')
CMD_BAUD = ('AT+BAUD{:d}', 'OK+Set:{:d}')
CMD_RESET = ('AT+RESET', 'OK+RESET')

BAUDS = [
    9600, #0
    19200,
    38400,
    57600,
    115200,
    4800,
    2400,
    1200,
    230400, #8
]

def set_module_baud(port: str, conn_baud: int, target_baud: int):
    target_index = BAUDS.index(target_baud)
    with Serial(port, conn_baud, timeout=.2) as ser:
        assert run_cmd(ser, CMD)
        assert run_cmd(ser, [s.format(target_index) for s in CMD_BAUD])
        assert run_cmd(ser, CMD_RESET)

def run_cmd(ser: Serial, cmd: tuple[str, str]) -> bool:
    ser.write(cmd[0].encode())
    out = ser.read(size=32).decode()
    print(f'CMD: {cmd[0]} > {out}')
    return out == cmd[1]
