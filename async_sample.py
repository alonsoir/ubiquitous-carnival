import asyncio
import time

import aiohttp
import requests

# https://medium.com/techtofreedom/9-levels-of-asynchronous-programming-in-python-3755f80403c9

async def producer(queue):
    for i in range(3):
        print(f"Producing {i}")
        await queue.put(i)
        await asyncio.sleep(2)  # simulate a delay for a time-consuming process


async def consumer(queue):
    while True:
        item = await queue.get()
        print(f"Consuming {item}")
        queue.task_done()


async def main():
    queue = asyncio.Queue()
    prod = asyncio.create_task(producer(queue))
    cons = asyncio.create_task(consumer(queue))

    await asyncio.gather(prod)
    await queue.join()
    cons.cancel()


asyncio.run(main())

async def task_1():
    print("Task 1 started")
    await asyncio.sleep(2)
    print("Task 1 finished")
    return "Result 1"

async def main():
    t1 = asyncio.create_task(task_1())
    t1.cancel()
    try:
        await t1
    except asyncio.CancelledError:
        print("Handled cancellation of Task 1")

asyncio.run(main())

semaphore = asyncio.Semaphore(5)

async def limited_task(n):
    async with semaphore:
        print(f'Task {n} started')
        await asyncio.sleep(1)
        print(f'Task {n} finished')

async def main():
    tasks = [limited_task(i) for i in range(10)]
    await asyncio.gather(*tasks)

asyncio.run(main())

async def slow_task():
    await asyncio.sleep(5)
    return "Task finished"

async def main():
    try:
        result = await asyncio.wait_for(slow_task(), timeout=2)
        print(result)
    except asyncio.TimeoutError:
        print("Task timed out!")

asyncio.run(main())

async def task_1():
    print("Task 1 started")
    try:
        await asyncio.sleep(2)
    except asyncio.CancelledError:
        print("Task 1 was cancelled")
        raise
    print("Task 1 finished")
    return "Result 1"

async def task_2():
    print("Task 2 started")
    await asyncio.sleep(1)
    print("Task 2 finished")
    return "Result 2"

async def main():
    t1 = asyncio.create_task(task_1())
    t2 = asyncio.create_task(task_2())

    # Wait for Task 2 to finish
    await t2

    # Cancel Task 1 before it finishes
    t1.cancel()

    # Wait for Task 1 to handle the cancellation
    try:
        await t1
    except asyncio.CancelledError:
        print("Handled cancellation of Task 1")

asyncio.run(main())

async def task_1():
    print("Task 1 started")
    await asyncio.sleep(2)
    print("Task 1 finished")
    return "Result 1"


async def task_2():
    print("Task 2 started")
    await asyncio.sleep(1)
    print("Task 2 finished")
    return "Result 2"


async def main():
    t1 = asyncio.create_task(task_1())
    t2 = asyncio.create_task(task_2())

    # Wait for both tasks to finish
    await t1
    await t2


asyncio.run(main())


async def task_1():
    print("Starting task 1")
    await asyncio.sleep(2) # simulate a slow I/O operation
    print("Task 1 done")

async def task_2():
    print("Starting task 2")
    await asyncio.sleep(1) # simulate another slow I/O operation
    print("Task 2 done")

async def main():
    await asyncio.gather(task_1(), task_2())

asyncio.run(main())


async def task_1():
    print("Task 1 started")
    await asyncio.sleep(2)
    print("Task 1 finished")
    return "Result 1"


async def task_2():
    print("Task 2 started")
    await asyncio.sleep(1)
    print("Task 2 finished")
    return "Result 2"


async def main():
    await asyncio.gather(task_1(), task_2())


asyncio.run(main())


# The urls list could be much longer
urls = ["http://example.com",
        "http://example.org",
        "http://example.net/",]

start_time = time.time()

for url in urls:
    response = requests.get(url)
    print(response.status_code)

print(f"Sync code cost {time.time() - start_time:.2f} seconds")
# Sync code cost 0.64 seconds

async def fetch_url(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            print(f"Status: {response.status}")

async def main():
    urls = ["http://example.com",
            "http://example.org",
            "http://example.net/",]
    start_time = time.time()
    await asyncio.gather(*(fetch_url(url) for url in urls))
    print(f"Async code cost {time.time() - start_time:.2f} seconds")

asyncio.run(main())
# Async code cost 0.22 seconds