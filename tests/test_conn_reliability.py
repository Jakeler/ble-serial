import sys
import subprocess
import time

ble_mac = sys.argv[1]

times = []
results = []

for i in range(100):
    print(f'RUN {i+1} > ', end='')
    t_start = time.perf_counter()
    run = subprocess.run(['ble-scan', '-d', ble_mac, '-t', '30'], 
        capture_output=True)
    t = time.perf_counter()-t_start
    times.append(t)

    fail = b'ERROR' in run.stdout.upper()
    results.append(not fail)

    if fail:
        print(f'FAILED after {t:.3f}')
        print(run.stdout.decode())
        break
    else:
        print(f'DONE in {t:.3f}s')
    # time.sleep(3)

print(f'success ratio {results.count(True)/len(results)*100:.1f} %')
print(results)
print(f'avg time {sum(times)/len(times)}s')
print(times)
