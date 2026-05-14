import numpy as np
import networkx as nx
from typing import Dict, Any, List

class DisasterSimulator:
    """
    Realistic stochastic disaster simulation engine.
    Models flood propagation, demand surges, infrastructure collapse, and cascading failures.
    """
    def __init__(self, districts: List[str], base_graph: nx.Graph, severity_multiplier: float = 1.0):
        self.districts = districts
        self.num_districts = len(districts)
        self.graph = base_graph.copy()
        self.base_graph = base_graph.copy()
        self.severity_multiplier = severity_multiplier
        self.current_period = 0
        
        # Initialize states
        self.flood_intensity = {d: 0.0 for d in districts}
        self.demand = {d: 0.0 for d in districts}
        self.infrastructure_damage = {d: 0.0 for d in districts}
        
    def initialize_disaster(self, epicenters: List[str], initial_severity: float = 0.8):
        """Start a disaster at specific epicenters."""
        for epicenter in epicenters:
            if epicenter in self.flood_intensity:
                self.flood_intensity[epicenter] = initial_severity * self.severity_multiplier
                self.demand[epicenter] = initial_severity * 1000 # Example scaling
                
        self._update_graph_edge_weights()
                
    def step(self) -> Dict[str, Any]:
        """Advance the simulation by one period."""
        self.current_period += 1
        
        new_flood = self.flood_intensity.copy()
        new_demand = self.demand.copy()
        new_damage = self.infrastructure_damage.copy()
        
        # Flood propagation: spreads to neighbors
        for node in self.graph.nodes():
            if self.flood_intensity[node] > 0.1:
                # Spread to neighbors
                for neighbor in self.graph.neighbors(node):
                    # Spread depends on connectivity and some randomness
                    spread_factor = np.random.uniform(0.1, 0.4)
                    increase = self.flood_intensity[node] * spread_factor
                    new_flood[neighbor] = min(1.0, new_flood[neighbor] + increase)
                    
            # Natural decay if no new spread
            new_flood[node] = max(0.0, new_flood[node] - np.random.uniform(0.01, 0.05))
            
            # Infrastructure damage accumulates based on flood
            damage_increase = new_flood[node] * np.random.uniform(0.05, 0.15)
            new_damage[node] = min(1.0, new_damage[node] + damage_increase)
            
            # Demand surge
            surge = new_flood[node] * np.random.uniform(10, 50) + new_damage[node] * np.random.uniform(5, 20)
            new_demand[node] += surge
            
        self.flood_intensity = new_flood
        self.demand = new_demand
        self.infrastructure_damage = new_damage
        
        # Dynamic road failure (cascading failures)
        failed_edges = self._update_graph_edge_weights()
        
        return {
            "period": self.current_period,
            "flood_intensity": self.flood_intensity,
            "demand": self.demand,
            "infrastructure_damage": self.infrastructure_damage,
            "failed_edges": failed_edges
        }
        
    def _update_graph_edge_weights(self) -> List[tuple]:
        """Update graph weights and simulate stochastic road collapse."""
        failed_edges = []
        for u, v, data in self.base_graph.edges(data=True):
            # Calculate failure probability based on damage of connected nodes
            node_damage = max(self.infrastructure_damage[u], self.infrastructure_damage[v])
            failure_prob = node_damage * 0.5 * self.severity_multiplier
            
            # Stochastic collapse
            if np.random.random() < failure_prob:
                if self.graph.has_edge(u, v):
                    self.graph.remove_edge(u, v)
                    failed_edges.append((u, v))
            else:
                # If not collapsed, cost increases dynamically
                base_cost = data.get('weight', 1.0)
                new_cost = base_cost * (1.0 + node_damage * 5.0)
                if self.graph.has_edge(u, v):
                    self.graph[u][v]['weight'] = new_cost
                    
        return failed_edges

    def get_routing_graph(self, vehicle_type: str) -> nx.Graph:
        """Get graph for routing. UAVs ignore road collapses."""
        if vehicle_type == 'uav':
            return self.base_graph.copy()
        return self.graph.copy()
