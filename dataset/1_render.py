import multiprocessing
import os
import threading
from itertools import batched
from time import sleep

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from playwright.sync_api import sync_playwright, Playwright
from tqdm import tqdm

from transform.bpmn_models import BPMNDiagram
from transform.bpmn_parser import parse_bpmn
from transform.preprocess import load_bpmn_all, b2img, b2lab

size = (1080, 1920)

def scale(diag: BPMNDiagram, sx, sy, sz) -> BPMNDiagram:
    def __bbox(o):
        x, y, w, h = o
        return (
            (x - sx) * sz,
            (y - sy) * sz,
            w * sz, h * sz,
        )
    for i in diag.processes:
        for j in i.elements:
            if not j.bbox: continue
            j.bbox = __bbox(j.bbox)
        for j in i.flows:
            if not j.lines: continue
            j.lines = [
                ((kx - sx) * sz, (ky - sy) * sz)
                for kx, ky in j.lines
            ]
        for j in i.lanes:
            if not j.bbox: continue
            j.bbox = __bbox(j.bbox)
        if i.bbox:
            i.bbox = __bbox(i.bbox)
    for j in diag.interprocess_flows:
        if not j.lines: continue
        j.lines = [
            ((kx - sx) * sz, (ky - sy) * sz)
            for kx, ky in j.lines
        ]
    return diag



def run(pw: Playwright, data):
    target = pw.firefox
    browser = target.launch(headless=False)
    context = browser.new_context(viewport=dict(width=size[1], height=size[0]))

    page = context.new_page()
    page.goto("http://localhost:11111/index.html")

    for fname in tqdm(data):
        txt = open(fname).read()
        models = parse_bpmn(txt)

        if len(models.links) < 2: continue

        output_f = b2img(fname)
        if os.path.isfile(output_f): continue

        page.evaluate(f"x => window.plot(x)", txt)
        sleep(0.1)
        page.locator("#canvas").screenshot(path=output_f, type='jpeg')
        pg = page.evaluate("() => window.xcanvas._cachedViewbox")

        models = scale(models, pg['x'], pg['y'], pg['scale'])
        models.save(b2lab(fname))

def serve():
    app = FastAPI()
    abs_static_path = os.path.join(os.path.dirname(__file__), "static/")
    app.mount("/", StaticFiles(directory=abs_static_path), name="")
    config = uvicorn.Config(app, host="0.0.0.0", port=11111, log_level="info")
    uvicorn.Server(config).run()


if __name__ == "__main__":
    threading.Thread(target=serve, daemon=True).start()

    tc = 20

    data = load_bpmn_all()
    bs = list(batched(data, len(data) // tc))

    with multiprocessing.Manager() as manager:
        def __proc(i):
            with sync_playwright() as playwright:
                run(playwright, i)

        with multiprocessing.Pool(tc) as pool:
            pool.map(__proc, bs)

