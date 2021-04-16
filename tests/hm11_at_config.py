from serial import Serial
from concurrent.futures import ThreadPoolExecutor
from time import sleep, perf_counter

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

# set_module_baud(0, 0)

with open('../README.md', 'rb') as f:
    CONTENT = f.read()
    # print(CONTENT)


def read_serial(port: str, conn_baud: int, expected_data: bytes):
    buffer = bytearray()
    timeout = .5
    with Serial(port, BAUDS[conn_baud], timeout=timeout) as ser:
        t1 = perf_counter()
        while True:
            chunk = ser.read(ser.in_waiting or 1)
            if len(chunk) < 1:
                break
            buffer += chunk
            print(f'Read {len(buffer)}')
        tt = perf_counter() - t1 - timeout # timeout is always included at the end
        rate = len(buffer)/tt
    print(f'Completed read {len(buffer)} bytes in {tt:.3f} s')
    print(f'Rate {rate:.2f} byte/s = {rate*8:.0f} bit/s = {rate*10:.0f} baud')

    return {
        'valid': expected_data == buffer,
        'loss_percent': (1 - len(buffer) / len(expected_data)) * 100
    }

def write_serial(port: str, conn_baud: int, data: bytes, chunk_size: int, delay: float):
    data_len = len(data)

    with Serial(port, BAUDS[conn_baud], timeout=1.0) as ser:
        t1 = perf_counter()
        for i in range(0, data_len, chunk_size):
            start, end = (i, i+chunk_size)
            ser.write(data[start:end])
            print(f'Written {end} bytes', end='\n')
            sleep(delay)
        ser.flush()
        tt = perf_counter()-t1
        rate = data_len/tt
    print() # do not overwrite replaced lines
    print(f'Completed write {data_len} bytes in {tt:.3f} s')
    print(f'Rate {rate:.2f} byte/s = {rate*8:.0f} bit/s = {rate*10:.0f} baud')


executor = ThreadPoolExecutor(max_workers=2)
futw = executor.submit(write_serial, PORT_UART, 0, CONTENT, 8, 0.0)
futr = executor.submit(read_serial, PORT_BLE, 0, CONTENT)
print(futr.result())