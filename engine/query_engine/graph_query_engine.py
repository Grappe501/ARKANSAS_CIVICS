from typing import List, Dict, Any


class GraphQueryEngine:
    def __init__(self, nodes: List[Dict], edges: List[Dict]):
        self.nodes = {n["id"]: n for n in nodes}
        self.edges = edges

        # Build adjacency
        self.forward = {}
        self.reverse = {}

        for e in edges:
            self.forward.setdefault(e["source"], []).append(e)
            self.reverse.setdefault(e["target"], []).append(e)

    def get_node(self, node_id: str):
        return self.nodes.get(node_id)

    def neighbors(self, node_id: str):
        return self.forward.get(node_id, [])

    def reverse_neighbors(self, node_id: str):
        return self.reverse.get(node_id, [])

    def traverse(self, start_id: str, depth: int = 2):
        visited = set()
        results = []

        def dfs(node_id, d):
            if d > depth or node_id in visited:
                return
            visited.add(node_id)

            for edge in self.neighbors(node_id):
                results.append(edge)
                dfs(edge["target"], d + 1)

        dfs(start_id, 0)
        return results