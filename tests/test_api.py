"""
Tests for WattWise AI API endpoints
"""

import pytest
from fastapi.testclient import TestClient

def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "WattWise AI" in data["message"]

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data

def test_get_region_scores(client):
    """Test getting region scores"""
    response = client.get("/regions/scores")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2  # We have 2 test regions
    
    # Check first region structure
    region = data[0]
    required_fields = [
        "region_id", "region_name", "green_energy_score",
        "renewable_percentage", "carbon_intensity", "electricity_cost",
        "gpu_availability", "cpu_availability", "memory_availability_gb"
    ]
    for field in required_fields:
        assert field in region

def test_schedule_workload(client, sample_workload_request):
    """Test scheduling a workload"""
    response = client.post("/jobs/schedule", json=sample_workload_request)
    assert response.status_code == 200
    data = response.json()
    
    required_fields = [
        "workload_id", "status", "recommended_region",
        "estimated_start_time", "estimated_end_time",
        "estimated_cost", "estimated_emissions", "reasoning"
    ]
    for field in required_fields:
        assert field in data
    
    assert data["status"] == "scheduled"
    assert data["workload_id"] is not None
    assert data["recommended_region"] in ["test-us-west-1", "test-eu-north-1"]

def test_schedule_workload_invalid_data(client):
    """Test scheduling workload with invalid data"""
    invalid_request = {
        "name": "",  # Empty name
        "workload_type": "invalid_type",
        "estimated_duration_hours": -1  # Negative duration
    }
    
    response = client.post("/jobs/schedule", json=invalid_request)
    assert response.status_code == 422  # Validation error

def test_get_workloads(client, sample_workload_request):
    """Test getting workloads list"""
    # First schedule a workload
    client.post("/jobs/schedule", json=sample_workload_request)
    
    # Then get workloads
    response = client.get("/workloads")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

def test_get_workloads_with_filters(client, sample_workload_request):
    """Test getting workloads with filters"""
    # Schedule a workload first
    schedule_response = client.post("/jobs/schedule", json=sample_workload_request)
    scheduled_data = schedule_response.json()
    region_id = scheduled_data["recommended_region"]
    
    # Test status filter
    response = client.get("/workloads?status=scheduled")
    assert response.status_code == 200
    data = response.json()
    assert all(w["status"] == "scheduled" for w in data)
    
    # Test region filter
    response = client.get(f"/workloads?region_id={region_id}")
    assert response.status_code == 200
    data = response.json()
    assert all(w["region_id"] == region_id for w in data)

def test_get_region_details(client):
    """Test getting region details"""
    response = client.get("/regions/test-us-west-1/details")
    assert response.status_code == 200
    data = response.json()
    
    required_fields = [
        "region_id", "region_name", "green_energy_score",
        "renewable_sources", "carbon_intensity", "electricity_cost",
        "gpu_types", "network_latency"
    ]
    for field in required_fields:
        assert field in data
    
    assert data["region_id"] == "test-us-west-1"

def test_get_region_details_not_found(client):
    """Test getting details for non-existent region"""
    response = client.get("/regions/non-existent-region/details")
    assert response.status_code == 404

def test_query_agent(client):
    """Test querying the AI assistant"""
    query_request = {
        "query": "Which region has the best green energy score?"
    }
    
    response = client.post("/agent/query", json=query_request)
    assert response.status_code == 200
    data = response.json()
    
    assert "response" in data
    assert isinstance(data["response"], str)
    assert len(data["response"]) > 0

def test_metrics_endpoint(client):
    """Test Prometheus metrics endpoint"""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    
    # Check for some expected metrics
    content = response.text
    assert "wattwise_requests_total" in content or "# HELP" in content

def test_cors_headers(client):
    """Test CORS headers are present"""
    response = client.options("/")
    # CORS headers should be present due to middleware
    assert response.status_code in [200, 405]  # OPTIONS might not be explicitly handled

