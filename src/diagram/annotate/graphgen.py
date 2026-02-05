from io import BytesIO

import iplotx as ipx
import networkx as nx
from matplotlib import pyplot as plt

from src.diagram.annotate.tools import bbox_center
from src.diagram.description_models import DiagramContents, GBPMNDiagram, GBPMNElementType, GBPMNFlowType

G_NODE_COLOR = {
    GBPMNElementType.TASK: "yellow",
    GBPMNElementType.GATEWAY: "red",
    GBPMNElementType.EVENT_START: "green",
    GBPMNElementType.EVENT_END: "gray",
    GBPMNElementType.EVENT_CATCH: "blue",
    GBPMNElementType.EVENT_THROW: "cyan",
}


class GraphBuilder:
    def __init__(self, contents: DiagramContents, diagram: GBPMNDiagram):
        self.contents = contents
        self.diagram = diagram
        self.graph = nx.DiGraph()
        self.push_nodes()
        self.push_edges()

    def push_nodes(self):
        for p in self.diagram.processes:
            for l in p.lanes:
                for o in l.objects:
                    self.graph.add_node(o.id, **o.model_dump())

    def push_edges(self):
        for (s1, s2), e in self.diagram.flows.items():
            if e.type == GBPMNFlowType.SEQUENCE:
                self.graph.add_edge(s1, s2, **e.model_dump())

    def create_layout(self):
        pos = {
            i: bbox_center(v['bbox'])
            for i, v in self.graph.nodes.data()
        }
        return nx.spring_layout(self.graph, pos=pos, fixed=self.graph.nodes)

    def visualize(self, sz=(640, 480), dpi=80):
        vertex_color = [G_NODE_COLOR[v['type']] for _, v in self.graph.nodes.data()]
        layout = self.create_layout()
        fig, ax = plt.subplots(figsize=(sz[0] / dpi, sz[1] / dpi), dpi=dpi)
        ipx.plot(self.graph, ax=ax, layout=layout, vertex_facecolor=vertex_color)
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=dpi, bbox_inches='tight')
        buf.seek(0)
        png_bytes = buf.getvalue()
        plt.close(fig)
        return png_bytes

    def __call__(self) -> nx.DiGraph:
        return self.graph
