from serial import Serial
from time import sleep, perf_counter

def read_serial(port: str, conn_baud: int, expected_data: bytes):
    buffer = bytearray()
    timeout = 1.0
    with Serial(port, conn_baud, timeout=timeout) as ser:
        t1 = perf_counter()
        while True:
            chunk = ser.read(ser.in_waiting or 1)
            if len(chunk) < 1:
                break
            buffer += chunk
            # print(f'Read {len(buffer)}')
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

    with Serial(port, conn_baud, timeout=1.0) as ser:
        t1 = perf_counter()
        for i in range(0, data_len, chunk_size):
            start, end = (i, i+chunk_size)
            ser.write(data[start:end])
            # print(f'Written {end} bytes', end='\n')
            sleep(delay)
        ser.flush()
        tt = perf_counter()-t1
        rate = data_len/tt
    print() # do not overwrite replaced lines
    print(f'Completed write {data_len} bytes in {tt:.3f} s')
    print(f'Rate {rate:.2f} byte/s = {rate*8:.0f} bit/s = {rate*10:.0f} baud')
