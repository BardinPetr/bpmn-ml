import os

from tqdm.contrib.concurrent import process_map


def pmap(fn, data, max_workers=os.cpu_count()):
    return process_map(fn, data, max_workers=max_workers, chunksize=len(data) // max_workers // 2)
