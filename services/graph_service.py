import networkx as nx
import string
import random


class GraphService:
    def __init__(self):
        self.graph = nx.Graph()
        self.directed = False
        self.weighted = False
        self.node_count = 0
        self.positions = {}
        self.edges_data = []

    def clear_graph(self):
        self.graph = nx.Graph()
        self.node_count = 0
        self.positions = {}
        self.edges_data = []
        self._rebuild_graph()

    def set_type(self, directed, weighted):
        changed = (directed != self.directed) or (weighted != self.weighted)
        self.directed = directed
        self.weighted = weighted
        if changed:
            self._rebuild_graph()

    def _rebuild_graph(self):
        self.graph = nx.DiGraph() if self.directed else nx.Graph()
        self.graph.add_nodes_from(self.positions.keys())
        for u, v, w in self.edges_data:
            if u in self.positions and v in self.positions:
                val = int(float(w)) if w not in [None, ""] else 1
                self.graph.add_edge(u, v, weight=val)

    def generate_node_id(self):
        letters = string.ascii_uppercase
        n = self.node_count
        name = ""
        temp_n = n
        while True:
            name = letters[temp_n % 26] + name
            temp_n = temp_n // 26 - 1
            if temp_n < 0:
                break
        self.node_count += 1
        return name

    def add_node(self, x, y, label=None):
        node_id = label if label else self.generate_node_id()
        if node_id not in self.positions:
            self.positions[node_id] = {
                "x": x + random.randint(-10, 10),
                "y": y + random.randint(-10, 10)
            }
        self._rebuild_graph()
        return node_id

    def add_edge(self, source, target, weight=1):
        if source in self.positions and target in self.positions:
            if self.directed:
                exists = any(u == source and v == target for u, v, w in self.edges_data)
            else:
                exists = any(
                    (u == source and v == target) or (u == target and v == source)
                    for u, v, w in self.edges_data
                )
            if not exists:
                try:
                    w = int(float(weight)) if weight not in [None, ""] else 1
                except:
                    w = 1
                self.edges_data.append((source, target, w))
                self._rebuild_graph()

    def remove_node(self, node_id):
        if node_id in self.positions:
            del self.positions[node_id]
            self.edges_data = [(u, v, w) for u, v, w in self.edges_data
                               if u != node_id and v != node_id]
            if not self.positions:
                self.node_count = 0
            self._rebuild_graph()

    def update_positions_from_elements(self, elements):
        if not elements:
            return
        for el in elements:
            if "position" in el and "id" in el.get("data", {}):
                node_id = el["data"]["id"]
                if node_id in self.positions:
                    self.positions[node_id] = el["position"]

    def get_elements(self):
        elements = []
        for node in self.graph.nodes:
            elements.append({
                "data": {
                    "id": str(node),
                    "label": str(node),
                    "directed": 1 if self.directed else 0,
                },
                "position": self.positions.get(node, {"x": 200, "y": 200})
            })
        for u, v, data in self.graph.edges(data=True):
            w = data.get("weight", 1)
            label = str(int(w)) if self.weighted else ""
            elements.append({
                "data": {
                    "id": f"edge-{u}-{v}",
                    "source": str(u),
                    "target": str(v),
                    "label": label,
                    "weight": w,
                }
            })
        return elements

    def get_info(self):
        return {
            "nodes": len(self.graph.nodes),
            "edges": len(self.graph.edges),
            "directed": self.directed,
            "weighted": self.weighted,
        }