import pytest
from concurrent.futures import ThreadPoolExecutor as TPE
from time import sleep

from hm11_at_config import reset_baud, set_module_baud
from serial_handler import read_serial, write_serial
from process_handler import run_ble_serial, signal_serial_end
from tools import eval_rx, Log, gen_test_data

from device_id import MacAddr
from endpoints import SerialPath, IP_TCP


@pytest.fixture
def tpe():
    return TPE(max_workers=3)

@pytest.fixture(params=[5*1024])
def test_data(request):
    return gen_test_data(request.param)

@pytest.fixture(scope="module", params=[19200, 38400])
def baud(request):
    return request.param

@pytest.fixture(scope="module")
def hm10_serial(baud):
    reset_baud(SerialPath.uart) # resets to 9600
    set_module_baud(SerialPath.uart, 9600, baud)


@pytest.fixture(params=[20])
def hm10_ble_client(tpe, request):
    futb = tpe.submit(run_ble_serial, MacAddr.hm10_serial, request.param)
    sleep(3) # wait for startup
    yield
    signal_serial_end()
    sleep(3) # wait for teardown


@pytest.mark.parametrize(
    "write_path, read_path", [
    (SerialPath.uart, SerialPath.ble),
    (SerialPath.ble, SerialPath.uart),
])
def test_uart_server(tpe: TPE, hm10_serial, baud, hm10_ble_client, test_data, write_path, read_path):
    packet_size = 64
    delay = packet_size*1/1000

    futw = tpe.submit(write_serial, write_path, baud, test_data, packet_size, delay)
    futr = tpe.submit(read_serial, read_path, baud, len(test_data))

    result = eval_rx(**futr.result(), expected_data=test_data)
    print(result)