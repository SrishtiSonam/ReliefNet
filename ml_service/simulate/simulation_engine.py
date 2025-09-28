import json
import numpy as np
import pandas as pd
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class SimulationEngine:
    def __init__(self, scenario_path: str):
        """
        Initialize simulation engine with scenario configuration
        
        Args:
            scenario_path: Path to JSON scenario file
        """
        with open(scenario_path, 'r') as f:
            self.scenario = json.load(f)
        
        self.districts = self._initialize_districts()
        self.fleet = self._initialize_fleet()
        self.road_graph = self._initialize_roads()
        
        # Results storage
        self.history = []
        
        logger.info(f"Initialized simulation with scenario: {self.scenario.get('name', 'unnamed')}")
        
    def _initialize_districts(self) -> Dict:
        """Initialize district states with random starting conditions"""
        districts = {}
        for i in range(1, 6):  # 5 districts
            district_id = f"D{i:03d}"
            districts[district_id] = {
                "district_id": district_id,
                "inventory": np.random.uniform(50, 150),
                "demand_last_period": np.random.uniform(10, 30),
                "backlog": np.random.uniform(0, 20),
                "avg_deprivation_time": np.random.uniform(1, 5),
                "road_access": "open",
                "coordinates": [28.6 + i*0.1, 77.2 + i*0.1]  # Delhi area coordinates
            }
        return districts
    
    def _initialize_fleet(self) -> List[Dict]:
        """Initialize vehicle fleet configuration"""
        return [
            {
                "class": "small_truck", 
                "capacity": 100, 
                "speed": 40, 
                "range_km": 500, 
                "count": 5,
                "cost_per_hour": 50,
                "fuel_efficiency": 8.0  # km per liter
            },
            {
                "class": "large_truck", 
                "capacity": 200, 
                "speed": 35, 
                "range_km": 600, 
                "count": 3,
                "cost_per_hour": 80,
                "fuel_efficiency": 6.0
            },
            {
                "class": "uav_light", 
                "capacity": 10, 
                "speed": 60, 
                "range_km": 50, 
                "count": 8,
                "cost_per_hour": 25,
                "fuel_efficiency": 20.0  # km per battery charge
            },
            {
                "class": "uav_heavy", 
                "capacity": 30, 
                "speed": 50, 
                "range_km": 80, 
                "count": 4,
                "cost_per_hour": 40,
                "fuel_efficiency": 15.0
            }
        ]
    
    def _initialize_roads(self) -> Dict:
        """Initialize road network graph"""
        return {
            "nodes": [
                {"id": f"D{i:03d}", "name": f"District_{i}", "coords": [28.6 + i*0.1, 77.2 + i*0.1]} 
                for i in range(1, 6)
            ],
            "edges": [
                {"u": "D001", "v": "D002", "distance": 12.4, "travel_time_mean": 0.5, "failure_prob": 0.02, "status": "open"},
                {"u": "D002", "v": "D003", "distance": 8.1, "travel_time_mean": 0.3, "failure_prob": 0.01, "status": "open"},
                {"u": "D003", "v": "D004", "distance": 15.2, "travel_time_mean": 0.7, "failure_prob": 0.03, "status": "open"},
                {"u": "D004", "v": "D005", "distance": 9.8, "travel_time_mean": 0.4, "failure_prob": 0.02, "status": "open"},
                {"u": "D001", "v": "D003", "distance": 18.7, "travel_time_mean": 0.8, "failure_prob": 0.04, "status": "open"},
                {"u": "D001", "v": "D004", "distance": 16.3, "travel_time_mean": 0.6, "failure_prob": 0.03, "status": "open"},
                {"u": "D002", "v": "D005", "distance": 20.5, "travel_time_mean": 0.9, "failure_prob": 0.05, "status": "open"}
            ]
        }
    
    def generate_demand(self, period: int) -> Dict[str, float]:
        """
        Generate demand for current period based on scenario parameters
        
        Args:
            period: Current time period
            
        Returns:
            Dictionary mapping district_id to demand value
        """
        demands = {}
        
        for district_id in self.districts:
            # Base demand with daily seasonality
            hour_of_day = period % 24
            seasonal_factor = 1.0 + 0.3 * np.sin(2 * np.pi * hour_of_day / 24)  # Peak around noon
            
            # Base demand with some randomness
            base_demand = np.random.gamma(2, 5) * seasonal_factor  
            
            # Check for surge events
            if period in self.scenario.get('shock_times', []):
                shock_districts = self.scenario.get('shock_multipliers', {}).get('districts', [])
                shock_mults = self.scenario.get('shock_multipliers', {}).get('mult', [])
                
                if district_id in shock_districts:
                    idx = shock_districts.index(district_id)
                    if idx < len(shock_mults):
                        base_demand *= shock_mults[idx]
                        logger.info(f"Surge event in {district_id}: demand multiplied by {shock_mults[idx]}")
            
            # Add some noise and ensure non-negative
            demand = max(0, base_demand + np.random.normal(0, 2))
            demands[district_id] = demand
            
        return demands
    
    def update_road_failures(self, period: int):
        """
        Update road network based on scheduled failures
        
        Args:
            period: Current time period
        """
        failures = self.scenario.get('road_failures', [])
        
        for failure in failures:
            if failure['time'] == period:
                # Find edge and mark as failed
                edge_nodes = failure['edge']
                for edge in self.road_graph['edges']:
                    if (edge['u'] in edge_nodes and edge['v'] in edge_nodes) or \
                       (edge['v'] in edge_nodes and edge['u'] in edge_nodes):
                        edge['status'] = 'failed'
                        edge['failure_prob'] = 1.0  # Complete failure
                        logger.info(f"Road failure at period {period}: {edge['u']} - {edge['v']}")
    
    def simulate_policy(self, policy: str, n_episodes: int) -> Tuple[Dict, List[Dict]]:
        """
        Run simulation episodes for a given policy
        
        Args:
            policy: Policy name ('dl_vfa', 'nn_vfa', 'heuristic', etc.)
            n_episodes: Number of episodes to run
            
        Returns:
            Tuple of (results_summary, episode_results)
        """
        episode_results = []
        
        logger.info(f"Starting simulation with policy '{policy}' for {n_episodes} episodes")
        
        for episode in range(n_episodes):
            episode_result = self._run_episode(policy, episode)
            episode_results.append(episode_result)
            
            if (episode + 1) % max(1, n_episodes // 10) == 0:
                logger.info(f"Completed episode {episode + 1}/{n_episodes}")
        
        # Aggregate results across episodes
        if episode_results:
            total_costs = [r['total_cost'] for r in episode_results]
            deprivation_times = [r['mean_deprivation'] for r in episode_results]
            coverage_rates = [r['demand_coverage'] for r in episode_results]
            max_deprivations = [r.get('max_deprivation', 0) for r in episode_results]
            
            results_summary = {
                "policy": policy,
                "episodes": n_episodes,
                "mean_cost": float(np.mean(total_costs)),
                "std_cost": float(np.std(total_costs)),
                "median_cost": float(np.median(total_costs)),
                "p90_cost": float(np.percentile(total_costs, 90)),
                "p95_cost": float(np.percentile(total_costs, 95)),
                "mean_deprivation": float(np.mean(deprivation_times)),
                "max_deprivation": float(np.mean(max_deprivations)),
                "demand_coverage": float(np.mean(coverage_rates)),
                "min_coverage": float(np.min(coverage_rates)),
                "scenario": self.scenario.get('name', 'unknown')
            }
        else:
            results_summary = {
                "policy": policy,
                "episodes": 0,
                "error": "No episodes completed successfully"
            }
        
        return results_summary, episode_results
    
    def _run_episode(self, policy: str, episode: int) -> Dict:
        """
        Run single simulation episode
        
        Args:
            policy: Policy to use for decision making
            episode: Episode number (for seeding)
            
        Returns:
            Dictionary with episode results
        """
        # Set episode-specific seed for reproducibility
        episode_seed = self.scenario.get('seed', 42) + episode
        np.random.seed(episode_seed)
        
        # Reset districts to initial state
        districts = self._initialize_districts()
        
        # Initialize tracking variables
        total_cost = 0
        deprivation_times = []
        total_demand = 0
        satisfied_demand = 0
        period_history = []
        
        periods = self.scenario.get('periods', 24)
        
        for period in range(periods):
            # Generate demand for this period
            demands = self.generate_demand(period)
            
            # Update road network (handle failures)
            self.update_road_failures(period)
            
            # Make policy decision
            allocations = self._make_policy_decision(districts, demands, policy, period)
            
            # Apply allocations and update states
            period_cost, period_deprivation, period_satisfied = self._apply_allocations(
                districts, demands, allocations
            )
            
            # Update tracking variables
            total_cost += period_cost
            deprivation_times.extend(period_deprivation)
            period_demand = sum(demands.values())
            total_demand += period_demand
            satisfied_demand += period_satisfied
            
            # Store period history
            period_history.append({
                "period": period,
                "total_demand": period_demand,
                "satisfied_demand": period_satisfied,
                "cost": period_cost,
                "allocations": len(allocations),
                "avg_deprivation": np.mean(period_deprivation) if period_deprivation else 0
            })
        
        # Calculate final metrics
        mean_deprivation = np.mean(deprivation_times) if deprivation_times else 0
        max_deprivation = np.max(deprivation_times) if deprivation_times else 0
        demand_coverage = satisfied_demand / total_demand if total_demand > 0 else 0
        
        return {
            "episode": episode,
            "policy": policy,
            "seed": episode_seed,
            "total_cost": total_cost,
            "mean_deprivation": mean_deprivation,
            "max_deprivation": max_deprivation,
            "demand_coverage": demand_coverage,
            "total_demand": total_demand,
            "satisfied_demand": satisfied_demand,
            "periods": periods,
            "period_history": period_history
        }
    
    def _make_policy_decision(self, districts: Dict, demands: Dict, policy: str, period: int) -> List[Dict]:
        """
        Make allocation decision based on specified policy
        
        Args:
            districts: Current district states
            demands: Predicted demands for this period
            policy: Policy name
            period: Current period
            
        Returns:
            List of allocation decisions
        """
        allocations = []
        
        if policy == "dl_vfa":
            # VFA-based decision: prioritize by backlog + predicted demand
            district_priorities = []
            for district_id, state in districts.items():
                priority = state['backlog'] + demands.get(district_id, 0)
                # Add urgency factor based on deprivation time
                urgency_factor = 1 + (state['avg_deprivation_time'] / 10)
                priority *= urgency_factor
                district_priorities.append((district_id, priority, state))
            
            # Sort by priority (highest first)
            district_priorities.sort(key=lambda x: x[1], reverse=True)
            
            # Allocate to top priority districts
            available_fleet = {v['class']: v['count'] for v in self.fleet}
            
            for district_id, priority, state in district_priorities:
                if priority > 15 and available_fleet['small_truck'] > 0:  # Threshold for allocation
                    allocations.append({
                        "district": district_id,
                        "truck_class": "small_truck",
                        "count": 1,
                        "eta_hours": np.random.uniform(1.5, 3.0),
                        "priority": priority
                    })
                    available_fleet['small_truck'] -= 1
                
                elif priority > 25 and available_fleet.get('uav_light', 0) > 0:
                    allocations.append({
                        "district": district_id,
                        "truck_class": "uav_light",
                        "count": 2,
                        "eta_hours": np.random.uniform(0.5, 1.5),
                        "priority": priority
                    })
                    available_fleet['uav_light'] -= 2
        
        elif policy == "nn_vfa":
            # Neural network VFA (similar logic but with different weights)
            district_scores = []
            for district_id, state in districts.items():
                # More complex scoring function (simulating NN output)
                base_score = state['backlog'] * 0.6 + demands.get(district_id, 0) * 0.4
                deprivation_penalty = state['avg_deprivation_time'] ** 1.5 * 2
                inventory_bonus = max(0, 100 - state['inventory']) * 0.1
                
                total_score = base_score + deprivation_penalty + inventory_bonus
                district_scores.append((district_id, total_score, state))
            
            # Sort by score
            district_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Allocate resources
            fleet_usage = {"small_truck": 0, "uav_light": 0}
            
            for district_id, score, state in district_scores:
                if score > 20 and fleet_usage["small_truck"] < 3:
                    allocations.append({
                        "district": district_id,
                        "truck_class": "small_truck",
                        "count": 1,
                        "eta_hours": np.random.uniform(2.0, 3.5),
                        "score": score
                    })
                    fleet_usage["small_truck"] += 1
        
        elif policy == "heuristic":
            # Simple pro-rata allocation based on need
            total_need = sum(districts[d]['backlog'] + demands.get(d, 0) for d in districts)
            
            if total_need > 0:
                available_capacity = sum(v['capacity'] * v['count'] for v in self.fleet[:2])  # Use first 2 vehicle types
                
                for district_id in districts:
                    need = districts[district_id]['backlog'] + demands.get(district_id, 0)
                    proportion = need / total_need
                    
                    if proportion > 0.15:  # Allocate if need > 15% of total
                        vehicle_count = max(1, int(proportion * 4))  # Scale allocation
                        
                        allocations.append({
                            "district": district_id,
                            "truck_class": "small_truck",
                            "count": min(vehicle_count, 2),  # Cap at 2 vehicles per district
                            "eta_hours": np.random.uniform(2.0, 4.0),
                            "proportion": proportion
                        })
        
        elif policy == "greedy":
            # Greedy policy: always allocate to district with highest immediate need
            if districts:
                max_need_district = max(districts.items(), 
                                      key=lambda x: x[1]['backlog'] + demands.get(x[0], 0))
                district_id, state = max_need_district
                
                allocations.append({
                    "district": district_id,
                    "truck_class": "small_truck",
                    "count": 2,
                    "eta_hours": np.random.uniform(1.5, 2.5),
                    "reason": "highest_need"
                })
        
        elif policy == "round_robin":
            # Round robin allocation
            district_ids = list(districts.keys())
            selected_district = district_ids[period % len(district_ids)]
            
            allocations.append({
                "district": selected_district,
                "truck_class": "small_truck",
                "count": 1,
                "eta_hours": np.random.uniform(2.0, 3.0),
                "reason": "round_robin"
            })
        
        # Default case - no allocations
        return allocations
    
    def _apply_allocations(self, districts: Dict, demands: Dict, allocations: List[Dict]) -> Tuple[float, List[float], float]:
        """
        Apply allocations and update district states
        
        Args:
            districts: District states (modified in place)
            demands: Current period demands
            allocations: List of allocation decisions
            
        Returns:
            Tuple of (period_cost, period_deprivation_times, satisfied_demand)
        """
        period_cost = 0
        period_deprivation = []
        satisfied_demand = 0
        
        # First, update demands and backlogs
        for district_id, demand in demands.items():
            if district_id in districts:
                districts[district_id]['demand_last_period'] = demand
                districts[district_id]['backlog'] += demand
        
        # Apply allocations
        for allocation in allocations:
            district_id = allocation['district']
            if district_id not in districts:
                continue
                
            truck_class = allocation['truck_class']
            count = allocation['count']
            eta_hours = allocation.get('eta_hours', 2.0)
            
            # Find vehicle specifications
            vehicle_spec = next((v for v in self.fleet if v['class'] == truck_class), None)
            if not vehicle_spec:
                continue
                
            capacity = vehicle_spec['capacity']
            cost_per_hour = vehicle_spec['cost_per_hour']
            
            total_capacity = capacity * count
            
            # Calculate delivery (arrives after ETA)
            current_backlog = districts[district_id]['backlog']
            satisfied = min(current_backlog, total_capacity)
            excess_capacity = total_capacity - satisfied
            
            # Update district state
            districts[district_id]['backlog'] -= satisfied
            districts[district_id]['inventory'] += excess_capacity
            
            satisfied_demand += satisfied
            
            # Calculate costs
            transport_cost = count * cost_per_hour * eta_hours
            fuel_cost = eta_hours * vehicle_spec.get('fuel_efficiency', 5.0) * 1.5  # Fuel price factor
            
            period_cost += transport_cost + fuel_cost
        
        # Update deprivation times for all districts
        for district_id, state in districts.items():
            if state['backlog'] > 0:
                state['avg_deprivation_time'] += 1  # Increment deprivation time
                period_deprivation.append(state['avg_deprivation_time'])
            else:
                # Reset deprivation time if no backlog
                state['avg_deprivation_time'] = max(0, state['avg_deprivation_time'] - 0.5)
        
        return period_cost, period_deprivation, satisfied_demand

def run_simulation(scenario: str, policy: str, n_episodes: int) -> Dict:
    """
    Main simulation runner function - entry point for FastAPI
    
    Args:
        scenario: Scenario name or path
        policy: Policy to evaluate
        n_episodes: Number of episodes to run
        
    Returns:
        Dictionary with results summary and output file path
    """
    try:
        # Handle scenario path
        if scenario.endswith('.json'):
            scenario_path = scenario
        else:
            scenario_path = f"data/scenarios/{scenario}.json"
        
        # Create default scenario if it doesn't exist
        if not os.path.exists(scenario_path):
            logger.info(f"Creating default scenario at {scenario_path}")
            default_scenario = {
                "name": "default",
                "description": "Default simulation scenario",
                "seed": 42,
                "periods": 24,
                "shock_times": [6, 7, 8],
                "shock_multipliers": {
                    "districts": ["D001", "D002"], 
                    "mult": [3.5, 2.1]
                },
                "road_failures": [
                    {"time": 12, "edge": ["D003", "D004"]}
                ]
            }
            
            os.makedirs(os.path.dirname(scenario_path), exist_ok=True)
            with open(scenario_path, 'w') as f:
                json.dump(default_scenario, f, indent=2)
        
        # Initialize and run simulation
        sim_engine = SimulationEngine(scenario_path)
        results_summary, episode_results = sim_engine.simulate_policy(policy, n_episodes)
        
        # Save detailed results to CSV
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_file = f"./artifacts/experiments/sim_{policy}_{timestamp}.csv"
        
        os.makedirs("./artifacts/experiments", exist_ok=True)
        
        # Convert episode results to DataFrame and save
        if episode_results:
            df = pd.DataFrame(episode_results)
            df.to_csv(output_file, index=False)
            logger.info(f"Results saved to {output_file}")
        else:
            # Create empty file for failed simulations
            pd.DataFrame().to_csv(output_file, index=False)
        
        return {
            "results_summary": results_summary,
            "output_file": output_file
        }
        
    except Exception as e:
        logger.error(f"Simulation failed: {str(e)}")
        
        # Return error results
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        error_file = f"./artifacts/experiments/sim_{policy}_error_{timestamp}.csv"
        
        return {
            "results_summary": {
                "policy": policy,
                "episodes": 0,
                "mean_cost": 0,
                "mean_deprivation": 0,
                "demand_coverage": 0,
                "error": str(e)
            },
            "output_file": error_file
        }

# Utility functions for analysis
def compare_policies(scenario: str, policies: List[str], n_episodes: int = 10) -> Dict:
    """
    Compare multiple policies on the same scenario
    
    Args:
        scenario: Scenario to use
        policies: List of policy names
        n_episodes: Episodes per policy
        
    Returns:
        Comparison results
    """
    results = {}
    
    for policy in policies:
        logger.info(f"Evaluating policy: {policy}")
        result = run_simulation(scenario, policy, n_episodes)
        results[policy] = result['results_summary']
    
    return {
        "scenario": scenario,
        "policies": results,
        "episodes_per_policy": n_episodes
    }

def analyze_sensitivity(base_scenario: str, parameter_variations: Dict, policy: str = "dl_vfa", n_episodes: int = 5) -> Dict:
    """
    Sensitivity analysis by varying scenario parameters
    
    Args:
        base_scenario: Base scenario file
        parameter_variations: Dict of parameter variations to test
        policy: Policy to use for analysis
        n_episodes: Episodes per variation
        
    Returns:
        Sensitivity analysis results
    """
    # This would implement parameter sensitivity analysis
    # Left as placeholder for advanced analysis
    pass

if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) >= 4:
        scenario = sys.argv[1]
        policy = sys.argv[2]
        n_episodes = int(sys.argv[3])
    else:
        scenario = "baseline"
        policy = "dl_vfa"
        n_episodes = 5
    
    print(f"Running simulation: scenario={scenario}, policy={policy}, episodes={n_episodes}")
    
    result = run_simulation(scenario, policy, n_episodes)
    
    print("\nResults Summary:")
    print(json.dumps(result['results_summary'], indent=2))
    print(f"\nDetailed results saved to: {result['output_file']}")