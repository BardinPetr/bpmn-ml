import asyncio

import ray
from ray import ObjectRef


def ray_put(data):
    handle = ray.put(data)
    return handle.binary().hex()


def ray_get(*handle_hex):
    handles = [ObjectRef.from_binary(bytes.fromhex(i)) for i in handle_hex]
    data = ray.get(handles)
    return data[0] if len(data) == 1 else data


def ray_aget(*handle_hex):
    handles = [ObjectRef.from_binary(bytes.fromhex(i)) for i in handle_hex]
    data = asyncio.gather(handles)
    return data[0] if len(data) == 1 else data
