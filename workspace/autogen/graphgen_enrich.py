import random
from dataclasses import dataclass, field
from typing import List

import networkx as nx

from workspace.autogen.description_models import GBPMNElementType, GBPMNElementSubType
from workspace.autogen.util import random_text


def choose(*args):
    return random.choice(args)


@dataclass
class Probs:
    group_sequence_length: List[float] = field(default_factory=lambda: [0, 0.3, 0.4, 0.25, 0.05])
    group_node_types: dict = field(default_factory=lambda: {"event": 0.5, "action": 0.5})


class GenGraphTransformer:
    def __init__(self):
        pass

    def __call__(self, graph) -> nx.DiGraph:
        self.transformed_graph = nx.DiGraph()
        self.original_graph = graph
        self._node_counter = 0

        for node in nx.topological_sort(self.original_graph):
            node_type = self.original_graph.nodes[node].get("type")
            self._transform_node(node)

        self._copy_edges()
        return self.transformed_graph

    def _transform_node(self, node):
        attrs = self.original_graph.nodes[node].copy()
        desc = None
        match attrs["type"]:
            case "action":
                desc = (GBPMNElementType.TASK, GBPMNElementSubType.TASK_OTHER)
            case "fan_out":
                desc = (GBPMNElementType.GATEWAY,
                        choose(GBPMNElementSubType.GATEWAY_EVENT,
                               GBPMNElementSubType.GATEWAY_EXCLUSIVE,
                               GBPMNElementSubType.GATEWAY_INCLUSIVE,
                               GBPMNElementSubType.GATEWAY_PARALLEL))
            case "fan_in":
                desc = (GBPMNElementType.GATEWAY,
                        choose(GBPMNElementSubType.GATEWAY_EXCLUSIVE,
                               GBPMNElementSubType.GATEWAY_INCLUSIVE))
            case "process_start":
                desc = (GBPMNElementType.EVENT_START,
                        choose(GBPMNElementSubType.EVENT_OTHER,
                               GBPMNElementSubType.EVENT_TIMER,
                               GBPMNElementSubType.EVENT_MESSAGE,
                               GBPMNElementSubType.EVENT_CONDITIONAL))
            case "process_end":
                desc = (GBPMNElementType.EVENT_END,
                        choose(GBPMNElementSubType.EVENT_OTHER,
                               GBPMNElementSubType.EVENT_ERROR))
            case "event":
                desc = (choose(GBPMNElementType.EVENT_THROW, GBPMNElementType.EVENT_CATCH),
                        choose(
                            GBPMNElementSubType.EVENT_OTHER,
                            GBPMNElementSubType.EVENT_TIMER,
                            GBPMNElementSubType.EVENT_MESSAGE,
                            GBPMNElementSubType.EVENT_CONDITIONAL,
                            GBPMNElementSubType.EVENT_ERROR
                        ))

        attrs["type"] = desc[0].value
        attrs["subtype"] = desc[1].value
        attrs["name"] = random_text()
        self.transformed_graph.add_node(node, **attrs)

    def _copy_edges(self):
        for u, v in self.original_graph.edges():
            u_type = self.original_graph.nodes[u].get("type")
            v_type = self.original_graph.nodes[v].get("type")
            data = {"name": random_text()}
            self.transformed_graph.add_edge(u, v, **data)
