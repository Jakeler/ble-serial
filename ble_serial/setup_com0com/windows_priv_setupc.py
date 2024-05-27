import os
import sys
import subprocess
import re

# For compatibility:
# https://support.microsoft.com/en-us/topic/howto-specify-serial-ports-larger-than-com9-db9078a5-b7b6-bf00-240f-f749ebfd913e
PORT_USER = 'COM9'
PORT_INTERNAL = 'BLE'

BIN = 'setupc.exe'

def cd_to_install():
    # com0com needs to read inf from install path
    path = sys.argv[1]
    print(f'Changing into {path}')
    os.chdir(path)

def check_list(port: str):
    print(f'\n> Checking port list for {port}')
    p = subprocess.run([BIN, 'list'], check=True, capture_output=True)
    stdout = p.stdout.decode()
    print(stdout)
    return re.compile(rf'\w* PortName={port}$', flags=re.MULTILINE).search(stdout)

def install():
    print('> Trying to create port pair')
    p = subprocess.run([BIN, 'install', 'PortName='+PORT_USER, 'PortName='+PORT_INTERNAL],
        check=True, capture_output=True)
    stdout = p.stdout.decode()
    print(stdout)

if __name__ == "__main__":
    try:
        cd_to_install()
        done = check_list(PORT_INTERNAL)
        if done:
            print(f'Found: {done.group(0)}')
            print('Setup already done!')
        else:
            print(f'{PORT_INTERNAL} port does not exist')

            if check_list(PORT_USER):
                raise Exception(f'Error: user port {PORT_USER} already in use')

            install()
            print('Setup done!')
    except Exception as e:
        print(e)
    finally:
        # Keep CMD open to show results
        input('\nHit any key to close')
