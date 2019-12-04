import time, threading

addons = ['Hello', 'world.', 'how', 'are', 'you?']
position = 0

def task(name, delay, mod=False):
    global position
    
    for n in range(5):
        for i in range(3_000_000*delay):
            pass
        if mod:
            position = n
        print(name, n, addons[position])
    return f"{name} DONE!"

threading.Thread(target=task, args=("One", 10)).start()
threading.Thread(target=task, args=("Two", 20)).start()
threading.Thread(target=task, args=("Three", 10, True)).start()