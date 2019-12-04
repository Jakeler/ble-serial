import asyncio, time

async def task(name, delay):
    for i in range(5):
        await asyncio.sleep(delay)
        print(name, i)
    return f"{name} DONE!"

async def start():
    r2 = task("One", 1.0)
    r1 = task("Two", 0.5)
    t2 = asyncio.create_task(r2)
    t1 = asyncio.create_task(r1)
    # all = asyncio.gather(
    #     task('Two', 0.5), 
    #     task('One', 1.0)
    # )
    for i in range(5):
        await asyncio.sleep(2)
        print("START", i)
    print(await t1, await t2)
    # print(await all)

asyncio.run(start())

