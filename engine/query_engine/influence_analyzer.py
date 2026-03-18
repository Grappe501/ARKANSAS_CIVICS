from collections import defaultdict


class InfluenceAnalyzer:
    def __init__(self, graph_engine):
        self.graph = graph_engine

    def bill_influence(self, bill_id: str):
        influences = defaultdict(int)

        edges = self.graph.reverse_neighbors(bill_id)

        for e in edges:
            if e["relationship_type"] == "sponsors":
                influences[e["source"]] += 3

        # committees
        for e in self.graph.neighbors(bill_id):
            if e["relationship_type"] == "referred_to":
                committee = e["target"]
                influences[committee] += 2

                members = self.graph.reverse_neighbors(committee)
                for m in members:
                    if m["relationship_type"] == "member_of":
                        influences[m["source"]] += 1

        return sorted(
            [{"node": k, "score": v} for k, v in influences.items()],
            key=lambda x: x["score"],
            reverse=True
        )