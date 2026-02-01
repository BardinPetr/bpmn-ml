import os
import random
import re
from typing import Optional, Tuple

from tqdm import tqdm

from transform.bpmn_parser import BPMNParser
from transform.utils import xhash

DRY = False

filterlist = {}


# filterlist = {i.strip().split('.')[0]
#               for i in open('del.list', 'r').read().strip().split('\n')}

def load_input():
    data = [
        (root, i)
        for root, _, files in os.walk("input")
        for i in files
    ]
    for loc, fname in tqdm(data):
        path = os.path.join(loc, fname)
        txt = open(path).read()
        uid = xhash(txt)
        if uid in filterlist: continue

        out_all = f"out_notation/{uid}.0.bpmn"
        if not DRY:
            if os.path.isfile(out_all): continue
            with open(out_all, "w") as f:
                f.write(txt.strip())


x_name_re = re.compile(r"^([0-9a-f]{64})\.(\d+)\.(\w+)$")


def f_identify(name) -> Optional[Tuple[str, int, str]]:
    if m := x_name_re.match(name):
        return m.group(1), int(m.group(2)), m.group(3)
    return None


def load_bpmn():
    return {
        m: os.path.join(root, i)
        for root, _, files in os.walk("out_notation")
        for i in files
        if (m := f_identify(i))
    }


def load_bpmn_all():
    return [
        v
        for (_, i, _), v in load_bpmn().items()
    ]


def load_bpmn_orig():
    return [
        v
        for (_, i, _), v in load_bpmn().items()
        if i == 0
    ]


def load_bpmn_augment():
    return [
        v
        for (_, i, _), v in load_bpmn().items()
        if i > 0
    ]


def drop_augment():
    if DRY: return
    for i in load_bpmn_augment():
        os.unlink(i)


ru_al = "".join(chr(i) for i in range(ord('а'), ord('я') + 1))
alphabet = ru_al + ru_al.upper() + " "


def name_transform(orig) -> str:
    d = random.choices(alphabet, k=len(orig))
    return ''.join(i if i in {'\n', '\t'} else j
                   for i, j in zip(orig, d))


def do_augment(txt, nonce) -> str:
    ET, root = BPMNParser.load_xml(txt)
    ET.register_namespace('', "http://www.omg.org/spec/BPMN/20100524/MODEL")
    ET.register_namespace('bpmndi', "http://www.omg.org/spec/BPMN/20100524/DI")
    ET.register_namespace('omgdc', "http://www.omg.org/spec/DD/20100524/DC")
    ET.register_namespace('omgdi', "http://www.omg.org/spec/DD/20100524/DI")
    for c in root.findall('.//{*}process/*') + root.findall('.//{*}collaboration/*'):
        if o_name := c.attrib.get('name', None):
            c.attrib['name'] = name_transform(o_name)
    res = ET.tostring(root, encoding='utf-8', xml_declaration=True).decode('utf-8')
    return res


def augment():
    if DRY: return
    data = load_bpmn_orig()
    for in_path in tqdm(data):
        txt = open(in_path).read()
        for step in range(10):
            out_path = in_path.replace(".0", f".{1 + step}")
            out = do_augment(txt, step)
            with open(out_path, "w") as f:
                f.write(out.strip())


def clean():
    if DRY: return
    for i in load_bpmn_all():
        try:
            os.unlink(i)
            os.unlink(b2lab(i))
            os.unlink(b2img(i))
        except:
            pass


def b2lab(x):
    return x.replace("_notation", "_label").replace(".bpmn", ".json")


def b2img(x):
    return x.replace("_notation", "_image").replace(".bpmn", ".jpg")


if __name__ == "__main__":
    if DRY:
        print("DRY RUN")
    clean()
    load_input()
    drop_augment()
    # augment()
