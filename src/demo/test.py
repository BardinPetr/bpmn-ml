import asyncio
import time
import uuid

import aiohttp

def nonce():
    return str(uuid.uuid4())

async def f(sess):
    n = nonce()
    t = time.time()
    print(f"> {n}")
    res = await sess.post("http://localhost:8000/target/process", json=dict(request=f"X{n}"))
    tid = (await res.json())
    tid = tid["task_id"]
    print(f"T {n} -- {tid}")

    while True:
        res = await sess.get(f"http://localhost:8000/target/status/{tid}")
        res = await res.json()
        if res['status'] == 'SUCCESS':
            break
        await asyncio.sleep(1)







    print(f"< {n} | {(time.time() - t) * 1000} ms")
    return res['result']

async def main():
    async with aiohttp.ClientSession() as sess:
        await sess.get("http://localhost:8000/analyzer")
        # tests = [
        #     f(sess) for i in range(3)
        # ]
        # tests = await asyncio.gather(*tests)
        # print(tests)

asyncio.run(main())
