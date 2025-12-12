"""
Database Manager for ReliefNet Demo System
Handles all SQLite database operations with India-specific disaster data
"""

import sqlite3
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any

# Database path
DB_DIR = Path(__file__).parent
DB_PATH = DB_DIR / "reliefnet.db"
SCHEMA_PATH = DB_DIR / "schema.sql"
SEED_PATH = DB_DIR / "seed_data.sql"


class DatabaseManager:
    """Manages all database operations for the demo system"""
    
    def __init__(self, db_path: str = str(DB_PATH)):
        self.db_path = db_path
        self.ensure_database()
    
    def ensure_database(self):
        """Create database and tables if they don't exist"""
        # Create directory if needed
        DB_DIR.mkdir(exist_ok=True)
        
        # Check if database exists
        db_exists = os.path.exists(self.db_path)
        
        # Create connection
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        
        if not db_exists:
            print(f"Creating new database at {self.db_path}")
            # Create schema
            with open(SCHEMA_PATH, 'r') as f:
                conn.executescript(f.read())
            
            # Load seed data
            with open(SEED_PATH, 'r') as f:
                conn.executescript(f.read())
            
            conn.commit()
            print("Database initialized with seed data")
        
        conn.close()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    # ==================== PUBLIC REQUESTS ====================
    
    def add_public_request(self, request_data: Dict[str, Any]) -> int:
        """
        Add a new public relief request
        Returns: request_id of the created request
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO public_requests 
            (name, phone, district, location, resource_type, quantity, severity_level, description, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            request_data.get('name'),
            request_data.get('phone'),
            request_data.get('district'),
            request_data.get('location'),
            request_data.get('resource_type'),
            request_data.get('quantity', 1),
            request_data.get('severity_level'),
            request_data.get('description', ''),
            request_data.get('status', 'pending')
        ))
        
        request_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return request_id
    
    def get_public_requests(self, status: Optional[str] = None, district: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get public requests with optional filtering"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM public_requests WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if district:
            query += " AND district = ?"
            params.append(district)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def update_request_status(self, request_id: int, new_status: str) -> bool:
        """Update status of a public request"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE public_requests 
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE request_id = ?
        """, (new_status, request_id))
        
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return affected > 0
    
    # ==================== ROAD BLOCKAGES ====================
    
    def add_road_blockage(self, blockage_data: Dict[str, Any]) -> int:
        """Add a new road blockage report"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO road_blockages 
            (district, location, latitude, longitude, reason, severity, description, reported_by, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            blockage_data.get('district'),
            blockage_data.get('location'),
            blockage_data.get('latitude'),
            blockage_data.get('longitude'),
            blockage_data.get('reason'),
            blockage_data.get('severity'),
            blockage_data.get('description', ''),
            blockage_data.get('reported_by', 'System'),
            blockage_data.get('status', 'active')
        ))
        
        blockage_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return blockage_id
    
    def get_road_blockages(self, district: Optional[str] = None, status: str = 'active') -> List[Dict]:
        """Get road blockages with optional filtering"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM road_blockages WHERE status = ?"
        params = [status]
        
        if district:
            query += " AND district = ?"
            params.append(district)
        
        query += " ORDER BY reported_at DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def clear_blockage(self, blockage_id: int) -> bool:
        """Mark a blockage as cleared"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE road_blockages 
            SET status = 'cleared', cleared_at = CURRENT_TIMESTAMP
            WHERE blockage_id = ?
        """, (blockage_id,))
        
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return affected > 0
    
    # ==================== WAREHOUSE STOCK ====================
    
    def get_warehouse_stock(self, district: Optional[str] = None) -> List[Dict]:
        """Get warehouse stock levels"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if district:
            cursor.execute("SELECT * FROM warehouse_stock WHERE district = ?", (district,))
        else:
            cursor.execute("SELECT * FROM warehouse_stock ORDER BY district")
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def update_warehouse_stock(self, warehouse_id: str, stock_updates: Dict[str, int]) -> bool:
        """Update warehouse stock levels"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Build dynamic update query
        update_fields = []
        params = []
        
        for field, value in stock_updates.items():
            if field in ['food_kg', 'water_liters', 'medical_units', 'shelter_kits', 'blankets']:
                update_fields.append(f"{field} = ?")
                params.append(value)
        
        if not update_fields:
            return False
        
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        params.append(warehouse_id)
        
        query = f"UPDATE warehouse_stock SET {', '.join(update_fields)} WHERE warehouse_id = ?"
        cursor.execute(query, params)
        
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return affected > 0
    
    # ==================== VEHICLE STATUS ====================
    
    def get_vehicles(self, status: Optional[str] = None, vehicle_type: Optional[str] = None) -> List[Dict]:
        """Get vehicle status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM vehicle_status WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if vehicle_type:
            query += " AND type = ?"
            params.append(vehicle_type)
        
        query += " ORDER BY vehicle_id"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def update_vehicle_status(self, vehicle_id: str, updates: Dict[str, Any]) -> bool:
        """Update vehicle status and location"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        update_fields = []
        params = []
        
        allowed_fields = ['status', 'current_latitude', 'current_longitude', 'assigned_district', 'battery_percent', 'fuel_percent']
        
        for field, value in updates.items():
            if field in allowed_fields:
                update_fields.append(f"{field} = ?")
                params.append(value)
        
        if not update_fields:
            return False
        
        update_fields.append("last_updated = CURRENT_TIMESTAMP")
        params.append(vehicle_id)
        
        query = f"UPDATE vehicle_status SET {', '.join(update_fields)} WHERE vehicle_id = ?"
        cursor.execute(query, params)
        
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return affected > 0
    
    # ==================== ALLOCATION HISTORY ====================
    
    def add_allocation_record(self, allocation_data: Dict[str, Any]) -> int:
        """Record an allocation decision for ML training/analysis"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO allocation_history 
            (district, demand_kg, allocated_kg, trucks_assigned, uavs_assigned, vfa_score, priority_score, urgency_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            allocation_data.get('district'),
            allocation_data.get('demand_kg'),
            allocation_data.get('allocated_kg'),
            allocation_data.get('trucks_assigned', 0),
            allocation_data.get('uavs_assigned', 0),
            allocation_data.get('vfa_score'),
            allocation_data.get('priority_score'),
            allocation_data.get('urgency_level')
        ))
        
        allocation_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return allocation_id
    
    def get_allocation_history(self, district: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """Get allocation history for analysis"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if district:
            cursor.execute("""
                SELECT * FROM allocation_history 
                WHERE district = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (district, limit))
        else:
            cursor.execute("""
                SELECT * FROM allocation_history 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]


# Singleton instance
db_manager = DatabaseManager()


# Convenience functions
def get_db():
    """Get database manager instance"""
    return db_manager


if __name__ == "__main__":
    # Test database initialization
    print("Initializing database...")
    db = DatabaseManager()
    
    print("\nTesting database operations...")
    
    # Test getting requests
    requests = db.get_public_requests(limit=5)
    print(f"Found {len(requests)} public requests")
    
    # Test getting warehouses
    warehouses = db.get_warehouse_stock()
    print(f"Found {len(warehouses)} warehouses")
    
    # Test getting vehicles
    vehicles = db.get_vehicles()
    print(f"Found {len(vehicles)} vehicles")
    
    # Test getting blockages
    blockages = db.get_road_blockages()
    print(f"Found {len(blockages)} active road blockages")
    
    print("\n✅ Database initialized successfully!")
