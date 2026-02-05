import base64

import networkx as nx
import numpy as np

from src.diagram.description_models import GBPMNElementType, GBPMNElementSubType

TYPE_MAP = {
    (GBPMNElementType.TASK, GBPMNElementSubType.TASK_OTHER): "bpmn:Task",
    (GBPMNElementType.GATEWAY, GBPMNElementSubType.GATEWAY_EVENT): "bpmn:EventBasedGateway",
    (GBPMNElementType.GATEWAY, GBPMNElementSubType.GATEWAY_EXCLUSIVE): "bpmn:ExclusiveGateway",
    (GBPMNElementType.GATEWAY, GBPMNElementSubType.GATEWAY_PARALLEL): "bpmn:ParallelGateway",
    (GBPMNElementType.GATEWAY, GBPMNElementSubType.GATEWAY_INCLUSIVE): "bpmn:InclusiveGateway",
}


def cfirst(x):
    return x[0].upper() + x[1:]


def b64(x):
    x = str(x)
    return base64.b64encode(x.encode()).decode()


def layout_pos(lay, uid, b_shift, b_range, b_scale, sz=(640, 480)):
    return (lay[uid] - b_shift) / b_range * b_scale * np.array(sz)


def layout_analyze(lay):
    all_pts = np.array(list(lay.values()))
    p_min, p_max = all_pts.min(axis=0), all_pts.max(axis=0)
    return dict(b_range=p_max - p_min, b_shift=p_min)


class GraphBPMNCodegen:
    def __init__(self):
        self.code = []

    def add(self, other):
        if isinstance(other, list):
            self.code.extend(other)
        else:
            self.code.append(other)

    def add_element(self, process_id, uid, name, loc, typ, subtyp):
        # (uid, name, bpmn_type, px, py, process_id)
        bpmn_tdef = ""
        bpmn_type = TYPE_MAP.get((typ, subtyp), None)
        if bpmn_type is None:
            bpmn_type = f"bpmn:{cfirst(typ)}"
            bpmn_tdef = f"bpmn:{cfirst(subtyp)}"
        px, py = loc
        name = b64(name)
        self.add(f"makeElement('{uid}', `{name}`, '{bpmn_type}', '{bpmn_tdef}', {px}, {py}, '{process_id}');")

    def add_edge(self, uid1, uid2, label):
        label = b64(label)
        self.add(f"makeLink('{uid1}', '{uid2}', `{label}`);")

    def __str__(self):
        return "\n".join(self.code)

    def __call__(self, g: nx.DiGraph, layout, scale=1, target_size=(640, 480)):
        self.code = []
        config = layout_analyze(layout)
        for i, data in g.nodes.items():
            self.add_element(
                process_id="0",
                uid=i,
                name=data['label'],
                loc=layout_pos(layout, i, b_scale=scale, sz=target_size, **config),
                typ=data['type'],
                subtyp=data['subtype'],
            )

        for (a, b), data in g.edges.items():
            self.add_edge(a, b, data['label'])
        return str(self)
