# reliefnet/ml_services/optimization/route_planner.py
import networkx as nx
import pandas as pd
from typing import List, Dict, Optional

class ReliefRoutePlanner:
    """
    Advanced routing service for disaster logistics.
    Optimizes for distance while heavily penalizing high-risk/failed road segments.
    """
    def __init__(self, road_edges: List[Dict]):
        self.G = nx.Graph()
        self.load_graph(road_edges)

    def load_graph(self, road_edges: List[Dict]):
        """Builds the graph from edge list."""
        for edge in road_edges:
            # Safest weight: distance adjusted by failure probability
            # If failure_prob is 1.0, weight becomes effectively infinite
            risk_penalty = 1.0 / (1.001 - edge.get("failure_probability", 0))
            weight = edge["distance_km"] * risk_penalty
            
            self.G.add_edge(
                edge["source"], 
                edge["target"], 
                weight=weight,
                distance=edge["distance_km"],
                risk=edge.get("failure_probability", 0)
            )

    def get_route(self, start: str, end: str) -> Optional[Dict]:
        """Returns the optimal path and its metrics."""
        try:
            path = nx.shortest_path(self.G, source=start, target=end, weight='weight')
            
            # Calculate total metrics
            total_dist = 0
            max_risk = 0
            for i in range(len(path) - 1):
                edge_data = self.G.get_edge_data(path[i], path[i+1])
                total_dist += edge_data["distance"]
                max_risk = max(max_risk, edge_data["risk"])
            
            return {
                "path": path,
                "total_distance_km": round(total_dist, 2),
                "max_edge_risk": round(max_risk, 4),
                "status": "SAFE" if max_risk < 0.4 else "CAUTION" if max_risk < 0.7 else "HIGH_RISK"
            }
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None

if __name__ == "__main__":
    # Example usage for standalone testing
    mock_edges = [
        {"source": "Mumbai", "target": "Pune", "distance_km": 150, "failure_probability": 0.1},
        {"source": "Pune", "target": "Satara", "distance_km": 100, "failure_probability": 0.8}, # High risk road
        {"source": "Mumbai", "target": "Nashik", "distance_km": 170, "failure_probability": 0.05},
        {"source": "Nashik", "target": "Satara", "distance_km": 250, "failure_probability": 0.1},
    ]
    planner = ReliefRoutePlanner(mock_edges)
    route = planner.get_route("Mumbai", "Satara")
    print(f"Optimal Route: {route}")
