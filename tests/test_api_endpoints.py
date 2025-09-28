# tests/test_api_endpoints.py
import pytest
import requests
import json
from fastapi.testclient import TestClient
import sys
import os

# Add ml_service to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ml_service'))

from main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "SDPDIAP ML Service" in response.json()["message"]

def test_forecast_batch():
    request_data = {
        "district_ids": ["D001", "D002"],
        "horizon": 6
    }
    response = client.post("/forecast/batch", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "forecasts" in data
    assert "D001" in data["forecasts"]
    assert "mean" in data["forecasts"]["D001"]

def test_value_estimate():
    request_data = {
        "post_decision_state": {
            "D001": {"inventory": 100, "backlog": 10}
        },
        "forecast_features": {
            "D001": {"surge_prob": 0.1}
        },
        "model": "dl_vfa"
    }
    response = client.post("/value/estimate", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "vfa_value" in data
    assert "explanation" in data

def test_optimize():
    request_data = {
        "current_state": {
            "D001": {"inventory": 100, "backlog": 20, "demand_last_period": 15}
        },
        "vfa_estimates": {"D001": 50.0},
        "fleet": [
            {"class": "small_truck", "capacity": 100, "count": 5}
        ],
        "constraints": {}
    }
    response = client.post("/optimize", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "allocations" in data
    assert "objective" in data

def test_models_list():
    response = client.get("/models")
    assert response.status_code == 200
    
    data = response.json()
    assert "models" in data

# tests/test_mip_solver.py
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ml_service'))

from optimize.mip_solver import solve_allocation_mip

def test_mip_solver():
    current_state = {
        "D001": {"inventory": 50, "backlog": 30, "demand_last_period": 25},
        "D002": {"inventory": 100, "backlog": 10, "demand_last_period": 15}
    }
    
    vfa_estimates = {"D001": 100.0, "D002": 50.0}
    
    fleet = [
        {"class": "small_truck", "capacity": 100, "speed": 40, "count": 3},
        {"class": "uav_light", "capacity": 10, "speed": 60, "count": 5}
    ]
    
    result = solve_allocation_mip(current_state, vfa_estimates, fleet)
    
    assert "allocations" in result
    assert "objective" in result
    assert "solve_info" in result
    assert result["objective"] >= 0

def test_mip_with_constraints():
    current_state = {"D001": {"inventory": 50, "backlog": 30}}
    vfa_estimates = {"D001": 100.0}
    fleet = [{"class": "small_truck", "capacity": 100, "count": 2}]
    
    constraints = {
        "lock_out": ["D001"],
        "vehicle_limits": {"small_truck": 1}
    }
    
    result = solve_allocation_mip(current_state, vfa_estimates, fleet, constraints)
    
    # Should have no allocations to locked out district
    d001_allocations = [a for a in result["allocations"] if a["district"] == "D001"]
    assert len(d001_allocations) == 0
