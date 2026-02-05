import random
import uuid
from dataclasses import dataclass
from typing import List, Tuple, Optional

import networkx as nx


@dataclass
class GraphConfig:
    max_nodes: int = 30
    min_nodes: int = 3
    max_depth: int = 6

    p_event: float = 0.2
    p_action: float = 0.2
    p_fan_out: float = 0.3
    p_fan_in: float = 0.2
    p_end: float = 0.1
    p_back_edge: float = 0.1

    fan_out_branches: Tuple[int, int] = (2, 3)
    fan_in_inputs: Tuple[int, int] = (2, 3)

    event_action_sequence: Tuple[int, int] = (1, 4)


class ProbabilisticGraphGenerator:
    def __init__(self, config: GraphConfig = None):
        self.config = config or GraphConfig()
        self.graph = nx.DiGraph()
        self.pending_branches: List[Tuple[str, int]] = []
        self.fan_in_candidates: List[str] = []
        self.event_action_nodes: List[str] = []

    def _create_node(self, node_type: str) -> str:
        node_id = f"{node_type}_{uuid.uuid4()}"
        self.graph.add_node(node_id, type=node_type)
        if node_type == "fan_in":
            self.fan_in_candidates.append(node_id)
        elif node_type in ["event", "action"]:
            self.event_action_nodes.append(node_id)
        return node_id

    def _select_next_type(self, current_type: str, depth: int) -> str:
        if depth >= self.config.max_depth or len(self.graph) >= self.config.max_nodes:
            return "process_end"

        weights = {
            "event": self.config.p_event,
            "action": self.config.p_action,
            "fan_out": self.config.p_fan_out,
            "fan_in": self.config.p_fan_in if len(self.pending_branches) > 1 else 0,
            "process_end": self.config.p_end if len(self.graph) > self.config.min_nodes else 0
        }

        probs = list(weights.values())
        if not (total := sum(probs)):
            return "process_end"
        probs = [p / total for p in probs]
        return random.choices(list(weights.keys()), weights=probs)[0]

    def _try_add_back_edge(self, source: str) -> bool:
        source_type = self.graph.nodes[source]["type"]
        if source_type in ["fan_out", "event", "action"]:
            return False
        if random.random() > self.config.p_back_edge:
            return False

        targets = [n for n in self.fan_in_candidates + self.event_action_nodes
                   if n != source and not nx.has_path(self.graph, n, source)]

        if targets:
            target = random.choice(targets)
            self.graph.add_edge(source, target)
            return True

        return False

    def _create_event_action_sequence(self, current: str, depth: int):
        seq_length = random.randint(*self.config.event_action_sequence)
        prev = current

        for i in range(seq_length):
            node_type = random.choice(["event", "action"])
            node = self._create_node(node_type)
            self.graph.add_edge(prev, node)
            prev = node

            if i == seq_length - 1:  # Last node in sequence
                self.pending_branches.append((node, depth + 1))
                self._try_add_back_edge(node)

    def __call__(self) -> Optional[nx.DiGraph]:
        start = self._create_node("process_start")
        self.pending_branches.append((start, 0))

        while self.pending_branches and len(self.graph) < self.config.max_nodes:
            current, depth = self.pending_branches.pop(0)
            current_type = self.graph.nodes[current]["type"]

            next_type = self._select_next_type(current_type, depth)

            if next_type == "fan_out":
                fan_out = self._create_node("fan_out")
                self.graph.add_edge(current, fan_out)

                num_branches = random.randint(*self.config.fan_out_branches)
                for _ in range(num_branches):
                    self.pending_branches.append((fan_out, depth + 1))

                self._try_add_back_edge(fan_out)

            elif next_type == "fan_in":
                fan_in = self._create_node("fan_in")

                num_inputs = min(random.randint(*self.config.fan_in_inputs),
                                 len(self.pending_branches) + 1)

                if num_inputs < self.config.fan_in_inputs[0]:
                    return self.generate()

                self.graph.add_edge(current, fan_in)
                for _ in range(num_inputs - 1):
                    if self.pending_branches:
                        source, _ = self.pending_branches.pop(0)
                        self.graph.add_edge(source, fan_in)

                self.pending_branches.append((fan_in, depth + 1))

            elif next_type == "process_end":
                end = self._create_node("process_end")
                self.graph.add_edge(current, end)

            elif next_type in ["event", "action"]:
                self._create_event_action_sequence(current, depth)

        for node, _ in self.pending_branches:
            node_props = self.graph.nodes[node]
            if node_props['type'] == 'fan_out':
                current_out = self.graph.out_degree(node)
                needed = self.config.fan_out_branches[0] - current_out
                for _ in range(needed):
                    self.graph.add_edge(node, self._create_node("process_end"))
            elif node_props['type'] == 'fan_in':
                return None
        return self.graph
