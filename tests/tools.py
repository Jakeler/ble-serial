from concurrent.futures import ThreadPoolExecutor as TPE
import csv

def gen_test_data(byte_amount: int):
    with open('../README.md', 'rb') as f:
        content = f.read()
        # print(CONTENT)

    while byte_amount > len(content):
        content += content
    return content[:byte_amount]


class Log:
    def __init__(self, filename: str):
        fieldnames = ['dir', 'rated_baud', 'packet_size', 'delay', 
            'valid', 'loss_percent', 'rx_bits', 'rx_baud']
        self.csvfile = open(filename, 'w', newline='')
        self.writer = csv.DictWriter(self.csvfile, fieldnames=fieldnames)
        self.writer.writeheader()

    def write(self, data: dict):
        self.writer.writerow(data)

    def close(self):
        self.csvfile.close()


# def run_test(exc: TPE, log: Log, dir: Dir, baud: int, packet_size: int, delay: float):
#     futw = executor.submit(write_serial, dir.write, baud, CONTENT, packet_size, delay)
#     futr = executor.submit(read_serial, dir.read, baud, CONTENT)

#     result = futr.result()
#     result.update({
#         'dir': str(dir),
#         'rated_baud': baud,
#         'packet_size': packet_size,
#         'delay': delay,
#     })
#     log.write(result)
#     print(result, end='\n\n')


def eval_rx(buffer: bytes, expected_data: bytes, total_time: float) -> dict:
    rate = len(buffer)/total_time

    print(f'Completed read {len(buffer)} bytes in {total_time:.3f} s')
    print(f'Rate {rate:.2f} byte/s = {rate*8:.0f} bit/s = {rate*10:.0f} baud')

    with open('/tmp/base.md', 'wb') as f:
        f.write(expected_data)
    with open('/tmp/buffer.md', 'wb') as f:
        f.write(buffer)

    assert expected_data == buffer
    return {
        'valid': expected_data == buffer,
        'loss_percent': (1 - len(buffer) / len(expected_data)) * 100,
        'rx_bits': int(rate*8),
        'rx_baud': int(rate*10),
    }
