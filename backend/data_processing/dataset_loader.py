"""
Efficient dataset loading with caching for ReliefNet
"""
import pandas as pd
import json
from pathlib import Path
from functools import lru_cache
import warnings
warnings.filterwarnings('ignore')

import sys
sys.path.append(str(Path(__file__).parent.parent))
from config import (
    DEMAND_HISTORY_PATH, WAREHOUSES_PATH, FLOOD_RISK_PATH,
    HISTORICAL_DISASTERS_PATH, DELIVERY_PATTERNS_PATH
)


class DatasetLoader:
    """Lazy loading and caching for large datasets"""
    
    def __init__(self):
        self._cache = {}
    
    @lru_cache(maxsize=10)
    def load_demand_history(self):
        """Load historical demand time series"""
        if not DEMAND_HISTORY_PATH.exists():
            raise FileNotFoundError(
                f"Demand history not found. Run preprocessing_scripts.py first."
            )
        
        df = pd.read_csv(DEMAND_HISTORY_PATH, parse_dates=['date'])
        return df
    
    @lru_cache(maxsize=10)
    def load_warehouses(self):
        """Load warehouse data"""
        if not WAREHOUSES_PATH.exists():
            raise FileNotFoundError(
                f"Warehouse data not found. Run preprocessing_scripts.py first."
            )
        
        df = pd.read_csv(WAREHOUSES_PATH)
        return df
    
    @lru_cache(maxsize=10)
    def load_flood_risk(self):
        """Load flood risk scores"""
        if not FLOOD_RISK_PATH.exists():
            return None
        
        df = pd.read_csv(FLOOD_RISK_PATH)
        return df
    
    @lru_cache(maxsize=10)
    def load_historical_disasters(self):
        """Load historical disaster records"""
        if not HISTORICAL_DISASTERS_PATH.exists():
            return None
        
        df = pd.read_csv(HISTORICAL_DISASTERS_PATH, parse_dates=['date'])
        return df
    
    @lru_cache(maxsize=10)
    def load_delivery_patterns(self):
        """Load delivery logistics patterns"""
        if not DELIVERY_PATTERNS_PATH.exists():
            return None
        
        df = pd.read_csv(DELIVERY_PATTERNS_PATH)
        return df
    
    def get_recent_demand(self, days=30):
        """Get demand data for recent N days"""
        df = self.load_demand_history()
        return df.tail(days)
    
    def get_warehouse_inventory(self, warehouse_id=None):
        """Get current warehouse inventory"""
        df = self.load_warehouses()
        
        if warehouse_id:
            return df[df['warehouse_id'] == warehouse_id]
        
        return df
    
    def clear_cache(self):
        """Clear all cached data"""
        self._cache.clear()
        self.load_demand_history.cache_clear()
        self.load_warehouses.cache_clear()
        self.load_flood_risk.cache_clear()
        self.load_historical_disasters.cache_clear()
        self.load_delivery_patterns.cache_clear()


# Global instance
loader = DatasetLoader()
