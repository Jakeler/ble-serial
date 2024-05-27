import argparse

def run_setup(path: str):
    import ctypes
    import sys
    import os

    script_path = os.path.dirname(__file__)
    res = ctypes.windll.shell32.ShellExecuteW(None, "runas", 
        sys.executable, f'{script_path}\\windows_priv_setupc.py "{path}"', None, 1)
    print('OK' if res == 42 else 'Error: higher privileges required')

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, 
        description='Setup required COM port pair')
    parser.add_argument('--install-path', default='C:/Program Files (x86)/com0com/',
        help='Installation directory of the null modem emulator')
    args = parser.parse_args()

    run_setup(args.install_path)
