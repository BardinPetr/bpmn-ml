import asyncio
import json
import random
import re
import time
from pathlib import Path
from typing import List

import httpx
import requests
from rich import print

from src.ingress.api.model import StatusRs, TaskStatus

base_url = "http://localhost:8000"


async def process(subsystem, tasks: List) -> StatusRs:
    async with httpx.AsyncClient(timeout=30) as client:
        ts = time.time()
        if subsystem == 'd2t':
            files = [
                ("files", (Path(f).name, open(f, "rb"), "image/jpeg"))
                for f in tasks
            ]
            rs = await client.post(f"{base_url}/submit/d2t",
                                   files=files,
                                   data=dict(parameters=json.dumps(dict(language='en', visualize=True)))
                                   )
        else:
            rs = await client.post(f"{base_url}/submit/t2d", json=[t.model_dump() for t in tasks])

        request_id = rs.json()["request_id"]
        print(f"> {request_id}")

        while True:
            rs = await client.get(f"{base_url}/status/{request_id}")
            status: StatusRs = StatusRs.model_validate(rs.json())
            if status.status in [TaskStatus.SUCCESS, TaskStatus.FAILURE]:
                break
            await asyncio.sleep(0.5)

        async def __load(x):
            res = await client.get(f"{base_url}/result/{request_id}/{x}")
            # fn = re.findall(r'filename="(.*)"', res.headers['content-disposition'])[0]
            fn = random.random()
            with open(f"./tmp/{x}_{fn}", "wb") as f:
                f.write(res.read())

        for task in status.tasks:
            await asyncio.gather(*[__load(i) for i in task.output_file_ids])

        print(f"< {request_id} {(time.time() - ts) * 1000:.0f}ms")
        return status

async def main():
    result = await process("d2t", [
        "/home/petr/projects/mltests/dataset/out_image/0e5e7c91e225dd48e344d35c90e62fa7e867890268dd94df219d8b2eff0356aa.0.jpg"
    ] * 1)
    print(result)
    # ts = time.time()
    # requests.get(f"{base_url}/analyzer")
    # print(time.time() - ts)


if __name__ == "__main__":
    asyncio.run(main())
