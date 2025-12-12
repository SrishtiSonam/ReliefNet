-- Seed data for ReliefNet Demo System
-- India-specific disaster management data

-- Warehouse Stock (Major Indian cities)
INSERT INTO warehouse_stock (warehouse_id, warehouse_name, district, state, latitude, longitude, food_kg, water_liters, medical_units, shelter_kits, blankets) VALUES
('WH001', 'Mumbai Central Warehouse', 'Mumbai', 'Maharashtra', 19.0760, 72.8777, 45000, 80000, 5000, 1200, 3000),
('WH002', 'Delhi Emergency Hub', 'New Delhi', 'Delhi', 28.6139, 77.2090, 38000, 70000, 4500, 1000, 2500),
('WH003', 'Chennai Relief Center', 'Chennai', 'Tamil Nadu', 13.0827, 80.2707, 42000, 75000, 4800, 1100, 2800),
('WH004', 'Kolkata Supply Depot', 'Kolkata', 'West Bengal', 22.5726, 88.3639, 40000, 72000, 4600, 1050, 2600),
('WH005', 'Bangalore Distribution Center', 'Bangalore', 'Karnataka', 12.9716, 77.5946, 35000, 65000, 4200, 950, 2400),
('WH006', 'Hyderabad Logistics Hub', 'Hyderabad', 'Telangana', 17.3850, 78.4867, 36000, 68000, 4300, 980, 2450),
('WH007', 'Ahmedabad Emergency Store', 'Ahmedabad', 'Gujarat', 23.0225, 72.5714, 33000, 62000, 4000, 900, 2300),
('WH008', 'Pune Relief Warehouse', 'Pune', 'Maharashtra', 18.5204, 73.8567, 32000, 60000, 3900, 880, 2200);

-- Vehicle Status (Trucks, UAVs, Ambulances)
INSERT INTO vehicle_status (vehicle_id, vehicle_name, type, capacity_kg, battery_percent, fuel_percent, current_latitude, current_longitude, assigned_district, status) VALUES
('TRK001', 'Mumbai Truck Alpha', 'truck', 5000, NULL, 85, 19.0760, 72.8777, 'Mumbai', 'available'),
('TRK002', 'Mumbai Truck Beta', 'truck', 5000, NULL, 90, 19.0850, 72.8850, 'Mumbai', 'in_transit'),
('TRK003', 'Delhi Truck Gamma', 'truck', 5000, NULL, 75, 28.6139, 77.2090, 'New Delhi', 'available'),
('TRK004', 'Chennai Truck Delta', 'truck', 5000, NULL, 80, 13.0827, 80.2707, 'Chennai', 'available'),
('TRK005', 'Kolkata Truck Epsilon', 'truck', 5000, NULL, 70, 22.5726, 88.3639, 'Kolkata', 'loading'),
('UAV001', 'Mumbai Drone Alpha', 'uav', 50, 95, NULL, 19.0760, 72.8777, 'Mumbai', 'available'),
('UAV002', 'Mumbai Drone Beta', 'uav', 50, 88, NULL, 19.0800, 72.8800, 'Mumbai', 'in_transit'),
('UAV003', 'Delhi Drone Gamma', 'uav', 50, 92, NULL, 28.6139, 77.2090, 'New Delhi', 'available'),
('UAV004', 'Chennai Drone Delta', 'uav', 50, 85, NULL, 13.0827, 80.2707, 'Chennai', 'available'),
('UAV005', 'Bangalore Drone Epsilon', 'uav', 50, 90, NULL, 12.9716, 77.5946, 'Bangalore', 'available'),
('AMB001', 'Mumbai Ambulance 1', 'ambulance', 500, NULL, 95, 19.0760, 72.8777, 'Mumbai', 'available'),
('AMB002', 'Delhi Ambulance 1', 'ambulance', 500, NULL, 88, 28.6139, 77.2090, 'New Delhi', 'in_transit');

-- Public Requests (Sample disaster relief requests)
INSERT INTO public_requests (name, phone, district, location, resource_type, quantity, severity_level, description, status) VALUES
('Rajesh Kumar', '+91-9876543210', 'Mumbai', 'Dharavi, Mumbai', 'food', 50, 'high', 'Flood affected area, 50 families need food supplies', 'processing'),
('Priya Sharma', '+91-9876543211', 'Mumbai', 'Kurla West, Mumbai', 'water', 100, 'critical', 'Water contamination, urgent need for clean water', 'approved'),
('Amit Patel', '+91-9876543212', 'Delhi', 'Yamuna Bank, Delhi', 'medical', 20, 'high', 'Medical supplies needed for flood victims', 'pending'),
('Sunita Reddy', '+91-9876543213', 'Chennai', 'Velachery, Chennai', 'shelter', 30, 'critical', 'Cyclone damage, families need temporary shelter', 'dispatched'),
('Mohammed Ali', '+91-9876543214', 'Kolkata', 'Howrah, Kolkata', 'blankets', 80, 'medium', 'Cold weather, need blankets for elderly', 'pending'),
('Lakshmi Iyer', '+91-9876543215', 'Bangalore', 'Electronic City, Bangalore', 'food', 40, 'medium', 'Landslide affected area', 'processing'),
('Vikram Singh', '+91-9876543216', 'Hyderabad', 'Old City, Hyderabad', 'water', 75, 'high', 'Water shortage due to pipeline damage', 'approved'),
('Anjali Desai', '+91-9876543217', 'Pune', 'Kothrud, Pune', 'medical', 15, 'high', 'First aid kits needed urgently', 'pending');

-- Road Blockages (Current obstacles)
INSERT INTO road_blockages (district, location, latitude, longitude, reason, severity, description, reported_by, status) VALUES
('Mumbai', 'Western Express Highway, Andheri', 19.1136, 72.8697, 'flood', 'critical', 'Highway completely submerged, impassable', 'Traffic Police Mumbai', 'active'),
('Chennai', 'Anna Salai, Guindy', 13.0067, 80.2206, 'flood', 'high', 'Waterlogging, slow traffic', 'Chennai Corporation', 'active'),
('Delhi', 'Ring Road, ITO', 28.6289, 77.2465, 'accident', 'medium', 'Multi-vehicle accident, one lane blocked', 'Delhi Traffic Police', 'active'),
('Kolkata', 'EM Bypass, Garia', 22.4697, 88.3903, 'landslide', 'high', 'Debris on road from hillside collapse', 'Kolkata Municipal Corp', 'active'),
('Pune', 'Mumbai-Pune Expressway, Lonavala', 18.7537, 73.4086, 'landslide', 'critical', 'Road blocked by rocks and mud', 'Highway Authority', 'active'),
('Bangalore', 'Outer Ring Road, Marathahalli', 12.9591, 77.6974, 'construction', 'low', 'Road repair work, expect delays', 'BBMP', 'active');

-- Allocation History (Past allocations for ML training)
INSERT INTO allocation_history (district, demand_kg, allocated_kg, trucks_assigned, uavs_assigned, vfa_score, priority_score, urgency_level) VALUES
('Mumbai', 8500, 8000, 3, 5, 0.85, 0.92, 'critical'),
('Chennai', 6200, 6200, 2, 3, 0.78, 0.85, 'high'),
('Kolkata', 5800, 5500, 2, 2, 0.72, 0.78, 'high'),
('Delhi', 4500, 4500, 1, 1, 0.68, 0.70, 'medium'),
('Bangalore', 3800, 3800, 1, 1, 0.65, 0.65, 'medium'),
('Hyderabad', 4200, 4000, 1, 2, 0.70, 0.72, 'medium'),
('Pune', 3500, 3500, 1, 0, 0.62, 0.60, 'low');
