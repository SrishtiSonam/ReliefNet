export interface District {
  id: string;
  name: string;
  pop_affected: number;
  Itn: number;
  htn: number;
  deprivation_time_hours: number;
  deprivation_cost: number;
  dt_t_t1: number;
  sigma_dt: number;
  forecast_quantiles: {
    p5: number;
    p25: number;
    p50: number;
    p75: number;
    p95: number;
  };
  surge_prob: number;
  neighbors: string[];
  spatial_influence_score: number;
  suggested_truck_units: number;
  suggested_truck_quantity: number;
  suggested_UAV_units: number;
  suggested_UAV_quantity: number;
  coordinates: [number, number];
}

export interface VehicleClass {
  id: string;
  name: string;
  capacity: number;
  cost: number;
  range_km?: number;
  speed_kmh: number;
  available: number;
  in_transit: number;
  charging?: number;
}

export interface Vehicle {
  id: string;
  class_id: string;
  status: 'available' | 'in_transit' | 'charging' | 'maintenance';
  battery_percent?: number;
  eta_hours?: number;
  current_location?: string;
}

export interface Road {
  id: string;
  from: string;
  to: string;
  status: 'open' | 'slow' | 'blocked';
  mean_travel_time: number;
  travel_time_variance: number;
  distance_km: number;
}

export interface Scenario {
  id: string;
  name: string;
  description: string;
  effects: {
    supply_drop_percent?: number;
    road_closures?: string[];
    demand_surge_districts?: string[];
    surge_multiplier?: number;
  };
  metrics: {
    total_deprivation_cost_change_percent: number;
    max_deprivation_time_change_hours: number;
    demand_coverage_change_percent: number;
  };
}

export const globalData = {
  ICW: 12400,
  current_epoch: 6,
  next_update_eta: "2025-09-28 13:00",
  total_districts: 8,
  high_risk_districts: 4,
};

export const districts: District[] = [
  {
    id: "D1",
    name: "Gorkha",
    pop_affected: 18000,
    Itn: 1200,
    htn: 600,
    deprivation_time_hours: 18,
    deprivation_cost: 2.31,
    dt_t_t1: 900,
    sigma_dt: 180,
    forecast_quantiles: { p5: 600, p25: 800, p50: 900, p75: 1100, p95: 1500 },
    surge_prob: 0.38,
    neighbors: ["D2", "D3"],
    spatial_influence_score: 0.12,
    suggested_truck_units: 0,
    suggested_truck_quantity: 0,
    suggested_UAV_units: 2,
    suggested_UAV_quantity: 400,
    coordinates: [84.6259, 28.0000]
  },
  {
    id: "D2",
    name: "Sindhupalchok",
    pop_affected: 22000,
    Itn: 800,
    htn: 1200,
    deprivation_time_hours: 24,
    deprivation_cost: 3.87,
    dt_t_t1: 1100,
    sigma_dt: 220,
    forecast_quantiles: { p5: 700, p25: 950, p50: 1100, p75: 1300, p95: 1800 },
    surge_prob: 0.52,
    neighbors: ["D1", "D4"],
    spatial_influence_score: 0.18,
    suggested_truck_units: 1,
    suggested_truck_quantity: 5000,
    suggested_UAV_units: 1,
    suggested_UAV_quantity: 200,
    coordinates: [85.7000, 27.9500]
  },
  {
    id: "D3",
    name: "Dhading",
    pop_affected: 15000,
    Itn: 1500,
    htn: 300,
    deprivation_time_hours: 12,
    deprivation_cost: 1.34,
    dt_t_t1: 750,
    sigma_dt: 150,
    forecast_quantiles: { p5: 500, p25: 650, p50: 750, p75: 900, p95: 1200 },
    surge_prob: 0.22,
    neighbors: ["D1", "D5"],
    spatial_influence_score: 0.08,
    suggested_truck_units: 0,
    suggested_truck_quantity: 0,
    suggested_UAV_units: 1,
    suggested_UAV_quantity: 200,
    coordinates: [84.9000, 27.8500]
  },
  {
    id: "D4",
    name: "Rasuwa",
    pop_affected: 12000,
    Itn: 900,
    htn: 800,
    deprivation_time_hours: 30,
    deprivation_cost: 5.69,
    dt_t_t1: 650,
    sigma_dt: 130,
    forecast_quantiles: { p5: 450, p25: 550, p50: 650, p75: 750, p95: 1000 },
    surge_prob: 0.15,
    neighbors: ["D2", "D6"],
    spatial_influence_score: 0.14,
    suggested_truck_units: 1,
    suggested_truck_quantity: 5000,
    suggested_UAV_units: 2,
    suggested_UAV_quantity: 400,
    coordinates: [85.3000, 28.2000]
  },
  {
    id: "D5",
    name: "Nuwakot",
    pop_affected: 16000,
    Itn: 1100,
    htn: 500,
    deprivation_time_hours: 15,
    deprivation_cost: 1.87,
    dt_t_t1: 800,
    sigma_dt: 160,
    forecast_quantiles: { p5: 550, p25: 700, p50: 800, p75: 950, p95: 1300 },
    surge_prob: 0.31,
    neighbors: ["D3", "D7"],
    spatial_influence_score: 0.10,
    suggested_truck_units: 0,
    suggested_truck_quantity: 0,
    suggested_UAV_units: 1,
    suggested_UAV_quantity: 200,
    coordinates: [85.1500, 27.9000]
  },
  {
    id: "D6",
    name: "Dolakha",
    pop_affected: 19000,
    Itn: 700,
    htn: 900,
    deprivation_time_hours: 21,
    deprivation_cost: 3.12,
    dt_t_t1: 950,
    sigma_dt: 190,
    forecast_quantiles: { p5: 650, p25: 850, p50: 950, p75: 1150, p95: 1500 },
    surge_prob: 0.44,
    neighbors: ["D4", "D8"],
    spatial_influence_score: 0.16,
    suggested_truck_units: 1,
    suggested_truck_quantity: 5000,
    suggested_UAV_units: 1,
    suggested_UAV_quantity: 200,
    coordinates: [86.1000, 27.6700]
  },
  {
    id: "D7",
    name: "Kavrepalanchok",
    pop_affected: 24000,
    Itn: 1300,
    htn: 700,
    deprivation_time_hours: 16,
    deprivation_cost: 2.14,
    dt_t_t1: 1200,
    sigma_dt: 240,
    forecast_quantiles: { p5: 800, p25: 1050, p50: 1200, p75: 1400, p95: 1900 },
    surge_prob: 0.36,
    neighbors: ["D5", "D8"],
    spatial_influence_score: 0.13,
    suggested_truck_units: 1,
    suggested_truck_quantity: 5000,
    suggested_UAV_units: 0,
    suggested_UAV_quantity: 0,
    coordinates: [85.5500, 27.6000]
  },
  {
    id: "D8",
    name: "Makwanpur",
    pop_affected: 21000,
    Itn: 1000,
    htn: 600,
    deprivation_time_hours: 14,
    deprivation_cost: 1.68,
    dt_t_t1: 1000,
    sigma_dt: 200,
    forecast_quantiles: { p5: 700, p25: 900, p50: 1000, p75: 1200, p95: 1600 },
    surge_prob: 0.28,
    neighbors: ["D6", "D7"],
    spatial_influence_score: 0.11,
    suggested_truck_units: 0,
    suggested_truck_quantity: 0,
    suggested_UAV_units: 2,
    suggested_UAV_quantity: 400,
    coordinates: [85.0500, 27.4000]
  }
];

export const vehicleClasses: VehicleClass[] = [
  {
    id: "truck-large",
    name: "Truck-Large",
    capacity: 5000,
    cost: 900,
    speed_kmh: 45,
    available: 6,
    in_transit: 2,
  },
  {
    id: "truck-light",
    name: "Truck-Light",
    capacity: 2000,
    cost: 400,
    speed_kmh: 60,
    available: 4,
    in_transit: 1,
  },
  {
    id: "uav-short",
    name: "UAV-ShortRange",
    capacity: 200,
    cost: 120,
    range_km: 25,
    speed_kmh: 80,
    available: 8,
    in_transit: 2,
    charging: 2,
  },
  {
    id: "uav-long",
    name: "UAV-LongRange",
    capacity: 500,
    cost: 300,
    range_km: 60,
    speed_kmh: 100,
    available: 4,
    in_transit: 1,
    charging: 1,
  }
];

export const vehicles: Vehicle[] = [
  { id: "T001", class_id: "truck-large", status: "available" },
  { id: "T002", class_id: "truck-large", status: "in_transit", eta_hours: 3.5, current_location: "D2" },
  { id: "T003", class_id: "truck-light", status: "available" },
  { id: "U001", class_id: "uav-short", status: "available", battery_percent: 95 },
  { id: "U002", class_id: "uav-short", status: "charging", battery_percent: 45 },
  { id: "U003", class_id: "uav-long", status: "in_transit", battery_percent: 70, eta_hours: 1.2, current_location: "D4" },
];

export const roads: Road[] = [
  {
    id: "R001",
    from: "CW",
    to: "D1",
    status: "open",
    mean_travel_time: 2.5,
    travel_time_variance: 0.3,
    distance_km: 45
  },
  {
    id: "R002",
    from: "CW",
    to: "D2",
    status: "slow",
    mean_travel_time: 3.2,
    travel_time_variance: 0.8,
    distance_km: 58
  },
  {
    id: "R003",
    from: "D1",
    to: "D2",
    status: "open",
    mean_travel_time: 1.8,
    travel_time_variance: 0.2,
    distance_km: 32
  },
  {
    id: "R004",
    from: "D1",
    to: "D3",
    status: "blocked",
    mean_travel_time: 4.5,
    travel_time_variance: 1.2,
    distance_km: 38
  }
];

export const scenarios: Scenario[] = [
  {
    id: "baseline",
    name: "Baseline",
    description: "Normal operations",
    effects: {},
    metrics: {
      total_deprivation_cost_change_percent: 0,
      max_deprivation_time_change_hours: 0,
      demand_coverage_change_percent: 0
    }
  },
  {
    id: "aftershock",
    name: "Aftershock Surge",
    description: "50% surge in D1 & D3 for first 3 epochs",
    effects: {
      demand_surge_districts: ["D1", "D3"],
      surge_multiplier: 1.5
    },
    metrics: {
      total_deprivation_cost_change_percent: 18,
      max_deprivation_time_change_hours: 24,
      demand_coverage_change_percent: -12
    }
  },
  {
    id: "supply_shock",
    name: "Supply Chain Disruption",
    description: "40% supply drop at central warehouse",
    effects: {
      supply_drop_percent: 40
    },
    metrics: {
      total_deprivation_cost_change_percent: 25,
      max_deprivation_time_change_hours: 18,
      demand_coverage_change_percent: -22
    }
  },
  {
    id: "road_closure",
    name: "Major Road Closure",
    description: "Two main roads blocked",
    effects: {
      road_closures: ["R001", "R002"]
    },
    metrics: {
      total_deprivation_cost_change_percent: 14,
      max_deprivation_time_change_hours: 8,
      demand_coverage_change_percent: -8
    }
  }
];

export const auditLogs = [
  {
    id: 1,
    timestamp: "2025-09-28 11:45:32",
    actor: "John Planner",
    action: "Modified allocation",
    details: "Reduced UAV units to D3 from 2 to 1",
    reason: "Resource constraint - UAV maintenance"
  },
  {
    id: 2,
    timestamp: "2025-09-28 11:30:15",
    actor: "System",
    action: "Generated allocation",
    details: "VFA + MIP optimization completed",
    reason: "Automated suggestion based on current state"
  },
  {
    id: 3,
    timestamp: "2025-09-28 11:15:00",
    actor: "Sarah Manager",
    action: "Approved plan",
    details: "Epoch 5 allocation plan finalized",
    reason: "All constraints satisfied, deprivation minimized"
  }
];