import numpy as np
from typing import Dict, List

class FairnessMetrics:
    """
    Computes fairness constraints and metrics for allocations.
    """
    
    @staticmethod
    def gini_coefficient(shortages: np.ndarray) -> float:
        """
        Calculate the Gini coefficient of a numpy array of shortages.
        0 means perfect equality (everyone has the same shortage).
        1 means perfect inequality (one district has all the shortage).
        """
        # Ensure non-negative
        x = np.abs(shortages)
        n = len(x)
        if n == 0 or np.sum(x) == 0:
            return 0.0
            
        # Sort values
        x = np.sort(x)
        
        # Calculate Gini coefficient
        index = np.arange(1, n + 1)
        gini = ((np.sum((2 * index - n  - 1) * x)) / (n * np.sum(x)))
        return float(gini)
        
    @staticmethod
    def max_min_fairness(shortages: np.ndarray) -> float:
        """
        Max-min fairness aims to maximize the minimum allocation,
        which is equivalent to minimizing the maximum shortage.
        Returns the maximum shortage value.
        """
        if len(shortages) == 0:
            return 0.0
        return float(np.max(shortages))
        
    @staticmethod
    def calculate_fairness_penalty(shortages: Dict[str, float]) -> float:
        """
        Calculate a composite fairness penalty for an RL reward function or optimization objective.
        Combines variance, Gini coefficient, and max shortage.
        """
        shortage_arr = np.array(list(shortages.values()))
        
        if len(shortage_arr) == 0:
            return 0.0
            
        variance = np.var(shortage_arr)
        gini = FairnessMetrics.gini_coefficient(shortage_arr)
        max_shortage = FairnessMetrics.max_min_fairness(shortage_arr)
        
        # Weighted combination
        # The scale depends on the shortage units (assuming 0-1 normalized here)
        penalty = 0.4 * variance + 0.3 * gini + 0.3 * max_shortage
        return float(penalty)
        
    @staticmethod
    def evaluate_allocation_bias(shortages: Dict[str, float], vulnerability_scores: Dict[str, float]) -> float:
        """
        Evaluates if the allocation is biased against vulnerable districts.
        Correlation between vulnerability and shortage. 
        Positive correlation means highly vulnerable districts have high shortages (Bad).
        """
        shortage_list = []
        vuln_list = []
        
        for district, short in shortages.items():
            if district in vulnerability_scores:
                shortage_list.append(short)
                vuln_list.append(vulnerability_scores[district])
                
        if len(shortage_list) < 2:
            return 0.0
            
        correlation = np.corrcoef(shortage_list, vuln_list)[0, 1]
        
        # If correlation is nan (e.g., zero variance), return 0
        if np.isnan(correlation):
            return 0.0
            
        return float(correlation)
