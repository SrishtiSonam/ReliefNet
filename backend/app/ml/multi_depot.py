"""
multi_depot.py  (B.6)
Multi-Depot Relief Supply Problem

Features:
    • Multiple warehouses: state capitals  (12 defaults) + post offices from DB
    • Each warehouse has its own inventory and replenishment rate
    • MIP assigns districts to warehouses and selects vehicle types
    • Haversine-based road-distance cost model

Formulation:
    min  Σ_{w,n} [ c^truck_{w,n} · y^truck_{w,n}  +  c^uav_{w,n} · y^uav_{w,n} ]

    s.t.
        Σ_w (y^truck_{w,n} · Q^T + y^uav_{w,n} · Q^U) ≥ demand_n   ∀n  [demand]
        Σ_n (y^truck_{w,n} · Q^T + y^uav_{w,n} · Q^U) ≤ I^w         ∀w  [inventory]
        y^{truck,uav}_{w,n} ∈ Z+

Adapted from: Vehicle Routing Problem (VRP) literature applied to
              disaster logistics (Balcik & Beamon, 2008).
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from app.utils.logger import get_logger

logger = get_logger(__name__)

# ─── Warehouse source tracking (Improvement 9) ───────────────────────────────
_USING_DEFAULT_WAREHOUSES: bool = False


def get_warehouse_source() -> str:
    """
    Returns 'database' if warehouses were loaded from MongoDB,
    or 'default_hardcoded' if the development fallback is active.
    Include this in simulation result metadata so operators know
    which warehouse set was used.
    """
    return "default_hardcoded" if _USING_DEFAULT_WAREHOUSES else "database"

try:
    import pulp
    PULP_AVAILABLE = True
except ImportError:
    PULP_AVAILABLE = False


# ─── Warehouse data class ─────────────────────────────────────────────────────
@dataclass
class Warehouse:
    id:              str
    name:            str
    state:           str
    latitude:        float
    longitude:       float
    inventory:       float          # Current stock (relief units)
    supply_rate:     float          # Mean units arriving per period
    is_post_office:  bool = False
    capacity:        float = 1e9    # Max storage capacity


@dataclass
class DistrictDemandNode:
    name:      str
    latitude:  float
    longitude: float
    demand:    float                # Required units this period


# ─── Distance utility ─────────────────────────────────────────────────────────
def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in km."""
    R   = 6371.0
    φ1  = math.radians(lat1)
    φ2  = math.radians(lat2)
    Δφ  = math.radians(lat2 - lat1)
    Δλ  = math.radians(lon2 - lon1)
    a   = math.sin(Δφ / 2) ** 2 + math.cos(φ1) * math.cos(φ2) * math.sin(Δλ / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def road_distance_km(lat1, lon1, lat2, lon2) -> float:
    """Approximate road distance = 1.3 × Haversine (standard India factor)."""
    return haversine(lat1, lon1, lat2, lon2) * 1.3


def unit_truck_cost(dist_km: float,
                    base_per_km: float = 50.0,
                    fixed_cost: float = 200.0) -> float:
    return fixed_cost + dist_km * base_per_km


def unit_uav_cost(dist_km: float,
                  base_per_km: float = 20.0,
                  fixed_cost: float = 50.0) -> float:
    return fixed_cost + dist_km * base_per_km


# ─── MIP solver ───────────────────────────────────────────────────────────────
def solve_multi_depot_mip(
    warehouses:    List[Warehouse],
    districts:     List[DistrictDemandNode],
    truck_cap:     float = 5_000.0,
    uav_cap:       float = 200.0,
    max_trucks_wn: int   = 5,
    max_uavs_wn:   int   = 10,
    time_limit_sec:int   = 60,
) -> Dict[str, List[Dict]]:
    """
    Solve the multi-depot allocation MIP.

    Returns
    -------
    {district_name: [
        {warehouse_id, warehouse_name, truck_units, uav_units, distance_km, cost}
    ]}
    """
    if not PULP_AVAILABLE:
        logger.warning("PuLP unavailable — using nearest-warehouse greedy.")
        return _greedy_multi_depot(warehouses, districts, truck_cap, uav_cap)

    W = len(warehouses)
    D = len(districts)
    if W == 0 or D == 0:
        return {d.name: [] for d in districts}

    # Pre-compute cost matrices
    c_truck = [[0.0] * D for _ in range(W)]
    c_uav   = [[0.0] * D for _ in range(W)]
    dist_km_mat = [[0.0] * D for _ in range(W)]

    for w, wh in enumerate(warehouses):
        for d_idx, dist in enumerate(districts):
            rd = road_distance_km(wh.latitude, wh.longitude, dist.latitude, dist.longitude)
            ed = haversine(wh.latitude, wh.longitude, dist.latitude, dist.longitude)
            dist_km_mat[w][d_idx] = rd
            c_truck[w][d_idx] = unit_truck_cost(rd)
            c_uav[w][d_idx]   = unit_uav_cost(ed)

    prob = pulp.LpProblem("multi_depot_flood_relief", pulp.LpMinimize)

    y_t = [[pulp.LpVariable(f"yt_{w}_{d}", lowBound=0, upBound=max_trucks_wn, cat="Integer")
             for d in range(D)] for w in range(W)]
    y_u = [[pulp.LpVariable(f"yu_{w}_{d}", lowBound=0, upBound=max_uavs_wn,   cat="Integer")
             for d in range(D)] for w in range(W)]

    # ── Objective ─────────────────────────────────────────────────────────────
    prob += pulp.lpSum(
        c_truck[w][d] * y_t[w][d] + c_uav[w][d] * y_u[w][d]
        for w in range(W) for d in range(D)
    )

    # ── C1: Demand satisfaction ───────────────────────────────────────────────
    for d_idx, dist in enumerate(districts):
        prob += (
            pulp.lpSum(
                y_t[w][d_idx] * truck_cap + y_u[w][d_idx] * uav_cap
                for w in range(W)
            ) >= dist.demand,
            f"demand_{d_idx}"
        )

    # ── C2: Warehouse inventory ───────────────────────────────────────────────
    for w, wh in enumerate(warehouses):
        prob += (
            pulp.lpSum(
                y_t[w][d_idx] * truck_cap + y_u[w][d_idx] * uav_cap
                for d_idx in range(D)
            ) <= wh.inventory,
            f"inventory_{w}"
        )

    prob.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=time_limit_sec, gapRel=0.02))

    # ── Extract results ───────────────────────────────────────────────────────
    result: Dict[str, List[Dict]] = {d.name: [] for d in districts}
    for d_idx, dist in enumerate(districts):
        for w, wh in enumerate(warehouses):
            nt = int(round(pulp.value(y_t[w][d_idx]) or 0))
            nu = int(round(pulp.value(y_u[w][d_idx]) or 0))
            if nt > 0 or nu > 0:
                result[dist.name].append({
                    "warehouse_id":   wh.id,
                    "warehouse_name": wh.name,
                    "warehouse_state":wh.state,
                    "truck_units":    float(nt * truck_cap),
                    "uav_units":      float(nu * uav_cap),
                    "distance_km":    round(dist_km_mat[w][d_idx], 2),
                    "cost":           round(c_truck[w][d_idx] * nt + c_uav[w][d_idx] * nu, 2),
                    "is_post_office": wh.is_post_office,
                })

    return result


# ─── Greedy fallback ──────────────────────────────────────────────────────────
def _greedy_multi_depot(
    warehouses: List[Warehouse],
    districts:  List[DistrictDemandNode],
    truck_cap:  float,
    uav_cap:    float,
) -> Dict[str, List[Dict]]:
    """Assign each district to the nearest warehouse that still has stock."""
    wh_inv  = {wh.id: wh.inventory for wh in warehouses}
    result  = {d.name: [] for d in districts}

    for dist in districts:
        remaining = dist.demand
        sorted_wh = sorted(
            warehouses,
            key=lambda wh: haversine(wh.latitude, wh.longitude,
                                      dist.latitude, dist.longitude)
        )
        for wh in sorted_wh:
            if remaining <= 0:
                break
            if wh_inv[wh.id] <= 0:
                continue
            send = min(wh_inv[wh.id], remaining)
            rd   = road_distance_km(wh.latitude, wh.longitude, dist.latitude, dist.longitude)
            n_trucks = math.ceil(send / truck_cap)
            cost = unit_truck_cost(rd) * n_trucks
            result[dist.name].append({
                "warehouse_id":    wh.id,
                "warehouse_name":  wh.name,
                "warehouse_state": wh.state,
                "truck_units":     send,
                "uav_units":       0.0,
                "distance_km":     round(rd, 2),
                "cost":            round(cost, 2),
                "is_post_office":  wh.is_post_office,
            })
            wh_inv[wh.id] -= send
            remaining      -= send

    return result


# ─── Database helpers ─────────────────────────────────────────────────────────
async def load_warehouses_from_db(default_stock: float = 50_000.0) -> List[Warehouse]:
    """
    Load warehouses from MongoDB `warehouses` collection.
    Falls back to 12 state-capital defaults if collection is empty.
    Post offices (if stored) are loaded as secondary depots.
    """
    from app.database import get_db
    db   = get_db()
    docs = await db.warehouses.find({}, {"_id": 0}).to_list(length=5000)

    warehouses: List[Warehouse] = []
    for d in docs:
        try:
            warehouses.append(Warehouse(
                id             = str(d.get("id", d.get("name", "wh"))),
                name           = str(d.get("name", "")),
                state          = str(d.get("state", "")),
                latitude       = float(d.get("latitude",  0)),
                longitude      = float(d.get("longitude", 0)),
                inventory      = float(d.get("inventory", default_stock)),
                supply_rate    = float(d.get("supply_rate", default_stock * 0.1)),
                is_post_office = bool(d.get("is_post_office", False)),
                capacity       = float(d.get("capacity", 1e9)),
            ))
        except (TypeError, ValueError) as exc:
            logger.warning(f"Skipping bad warehouse record: {exc}")

    if not warehouses:
        global _USING_DEFAULT_WAREHOUSES
        _USING_DEFAULT_WAREHOUSES = True
        logger.warning(
            "WARNING: No warehouses found in DB — falling back to hardcoded state "
            "capitals. This is not suitable for production."
        )
        warehouses = default_state_capital_warehouses(default_stock)

    return warehouses


def default_state_capital_warehouses(stock: float = 50_000.0) -> List[Warehouse]:
    """
    12 pre-configured state capital warehouses covering flood-prone regions.
    """
    capitals = [
        ("wh_kerala",      "Thiruvananthapuram WH", "Kerala",          8.5241,  76.9366),
        ("wh_karnataka",   "Bengaluru WH",           "Karnataka",      12.9716,  77.5946),
        ("wh_tamilnadu",   "Chennai WH",             "Tamil Nadu",     13.0827,  80.2707),
        ("wh_andhra",      "Amaravati WH",           "Andhra Pradesh", 16.5062,  80.6480),
        ("wh_telangana",   "Hyderabad WH",           "Telangana",      17.3850,  78.4867),
        ("wh_odisha",      "Bhubaneswar WH",         "Odisha",         20.2961,  85.8245),
        ("wh_westbengal",  "Kolkata WH",             "West Bengal",    22.5726,  88.3639),
        ("wh_assam",       "Guwahati WH",            "Assam",          26.1445,  91.7362),
        ("wh_bihar",       "Patna WH",               "Bihar",          25.5941,  85.1376),
        ("wh_gujarat",     "Gandhinagar WH",         "Gujarat",        23.2156,  72.6369),
        ("wh_maharashtra", "Mumbai WH",              "Maharashtra",    19.0760,  72.8777),
        ("wh_up",          "Lucknow WH",             "Uttar Pradesh",  26.8467,  80.9462),
    ]
    return [
        Warehouse(
            id           = c[0],
            name         = c[1],
            state        = c[2],
            latitude     = c[3],
            longitude    = c[4],
            inventory    = stock,
            supply_rate  = stock * 0.1,
            is_post_office = False,
            capacity     = stock * 3,
        )
        for c in capitals
    ]