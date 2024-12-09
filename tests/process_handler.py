import subprocess
import os
import signal

# Needs start after reset of set_module_baud()
def run_ble_serial(mac, mtu, write_resp=False):
    terminal = 'konsole -e'
    binary = 'ble-serial'
    write_with_resp = '--write-with-response' if write_resp else '' 
    return subprocess.run(f'{terminal} {binary} -d {mac} -v --mtu {mtu} {write_with_resp}', 
        shell=True, check=True)

def signal_serial_end():
    pid = subprocess.check_output(['pgrep', 'ble-serial'])
    # print(f'Got PID {pid}')
    os.kill(int(pid), signal.SIGINT)