-- SQLite Database Schema for ReliefNet Demo System
-- All data is India-specific for disaster management demonstration

CREATE TABLE IF NOT EXISTS public_requests (
    request_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT,
    district TEXT NOT NULL,
    location TEXT NOT NULL,
    resource_type TEXT NOT NULL CHECK(resource_type IN ('food', 'water', 'medical', 'shelter', 'blankets')),
    quantity INTEGER DEFAULT 1,
    severity_level TEXT NOT NULL CHECK(severity_level IN ('low', 'medium', 'high', 'critical')),
    description TEXT,
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'processing', 'approved', 'dispatched', 'delivered', 'rejected')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS road_blockages (
    blockage_id INTEGER PRIMARY KEY AUTOINCREMENT,
    district TEXT NOT NULL,
    location TEXT NOT NULL,
    latitude REAL,
    longitude REAL,
    reason TEXT CHECK(reason IN ('flood', 'landslide', 'accident', 'construction', 'protest', 'other')),
    severity TEXT NOT NULL CHECK(severity IN ('low', 'medium', 'high', 'critical')),
    description TEXT,
    reported_by TEXT,
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'cleared', 'partial')),
    reported_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    cleared_at DATETIME
);

CREATE TABLE IF NOT EXISTS warehouse_stock (
    warehouse_id TEXT PRIMARY KEY,
    warehouse_name TEXT NOT NULL,
    district TEXT NOT NULL,
    state TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    food_kg INTEGER DEFAULT 0,
    water_liters INTEGER DEFAULT 0,
    medical_units INTEGER DEFAULT 0,
    shelter_kits INTEGER DEFAULT 0,
    blankets INTEGER DEFAULT 0,
    capacity_kg INTEGER DEFAULT 50000,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS vehicle_status (
    vehicle_id TEXT PRIMARY KEY,
    vehicle_name TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('truck', 'uav', 'ambulance', 'boat')),
    capacity_kg INTEGER NOT NULL,
    battery_percent INTEGER CHECK(battery_percent BETWEEN 0 AND 100),
    fuel_percent INTEGER CHECK(fuel_percent BETWEEN 0 AND 100),
    current_latitude REAL,
    current_longitude REAL,
    assigned_district TEXT,
    status TEXT DEFAULT 'available' CHECK(status IN ('available', 'in_transit', 'loading', 'maintenance', 'unavailable')),
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS allocation_history (
    allocation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    district TEXT NOT NULL,
    demand_kg INTEGER NOT NULL,
    allocated_kg INTEGER NOT NULL,
    trucks_assigned INTEGER DEFAULT 0,
    uavs_assigned INTEGER DEFAULT 0,
    vfa_score REAL,
    priority_score REAL,
    urgency_level TEXT CHECK(urgency_level IN ('low', 'medium', 'high', 'critical')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_requests_status ON public_requests(status);
CREATE INDEX IF NOT EXISTS idx_requests_district ON public_requests(district);
CREATE INDEX IF NOT EXISTS idx_blockages_district ON road_blockages(district);
CREATE INDEX IF NOT EXISTS idx_blockages_status ON road_blockages(status);
CREATE INDEX IF NOT EXISTS idx_warehouse_district ON warehouse_stock(district);
CREATE INDEX IF NOT EXISTS idx_vehicle_status ON vehicle_status(status);
CREATE INDEX IF NOT EXISTS idx_allocation_district ON allocation_history(district);
