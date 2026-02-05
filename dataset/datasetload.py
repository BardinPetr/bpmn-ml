import os
import re

from dataset.bpmn_models import BPMNDiagram
from src.utils import pmap


def load_text_ds(diag: BPMNDiagram):
    return [
        dict(
            text=re.sub(r"\s+", " ", n),
            box=i.bboxi,
            pos=i.bboxc
        )
        for p in diag.processes
        for i in p.elements
        if (n := i.name) and len(n) > 3 and i.bbox
    ]


def load(x):
    idr, ldr, label_file = x
    diag = BPMNDiagram.from_json(open(os.path.join(ldr, label_file), 'r').read())
    return dict(
        hash=label_file.split('.')[0],
        diagram=diag,
        textdetect=load_text_ds(diag),
        image=os.path.join(idr, label_file.replace(".json", ".jpg")),
    )


def load_dataset(base_dir):
    base_dir = os.path.abspath(base_dir)
    imdir, ladir = os.path.join(base_dir, 'out_image'), os.path.join(base_dir, 'out_label')
    return pmap(load, [(imdir, ladir, x) for x in os.listdir(ladir)])
