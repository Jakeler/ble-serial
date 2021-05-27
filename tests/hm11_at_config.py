from serial import Serial
from time import sleep

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
    print(f'Changing baud {conn_baud} > {target_baud}')
    target_index = BAUDS.index(target_baud)
    with Serial(port, conn_baud, timeout=.2) as ser:
        for _ in range(5):
            if run_cmd(ser, CMD):
                break
        assert run_cmd(ser, [s.format(target_index) for s in CMD_BAUD])
        assert run_cmd(ser, CMD_RESET)

def reset_baud(port: str):
    for b in BAUDS:
        try:
            set_module_baud(port, b, 9600)
            break
        except AssertionError:
            print(f'{b} was not correct...\n')

def run_cmd(ser: Serial, cmd: tuple[str, str]) -> bool:
    ser.write(cmd[0].encode())
    out = ser.read(size=32).decode()
    print(f'CMD: {cmd[0]} > {out}')
    return out == cmd[1]
