import socket
from time import sleep, perf_counter

def read_tcp(addr: str, port: int, expected_size: int) -> dict:
    buffer = bytearray()
    timeout = 8.0

    with socket.socket() as test_client:
        test_client.settimeout(timeout)
        test_client.connect((addr, port))
        print(f'Connected to {test_client}')

        t1 = perf_counter()
        while True:
            try:
               buffer += test_client.recv(1024)
            except TimeoutError:
                break

            buffer_size = len(buffer)
            print(f'\rReceived {buffer_size} / {expected_size} = {buffer_size/expected_size*100:.2f} %', end='')
        print()
        total_time = perf_counter() - t1 - timeout # timeout is always included at the end
    
    return {
        'total_time': total_time, 
        'buffer': buffer
    }

def write_tcp(addr: str, port: int, data: bytes, chunk_size: int, delay: float):
    data_len = len(data)
    timeout = 1.0

    with socket.socket() as test_client:
        test_client.settimeout(timeout)
        test_client.connect((addr, port))
        print(f'Connected to {test_client}')

        t1 = perf_counter()
        for i in range(0, data_len, chunk_size):
            start, end = (i, i+chunk_size)
            test_client.send(data[start:end])
            # print(f'Written {end} bytes', end='\n')
            sleep(delay)

        total_time = perf_counter()-t1
        rate = data_len/total_time
    
    print() # do not overwrite replaced lines
    print(f'Completed write {data_len} bytes in {total_time:.3f} s')
    print(f'Rate {rate:.2f} byte/s = {rate*8:.0f} bit/s = {rate*10:.0f} baud')