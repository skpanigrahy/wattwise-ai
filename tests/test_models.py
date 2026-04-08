"""
Tests for WattWise AI database models
"""

import pytest
from datetime import datetime
from models.database import Region, Workload, EnergyData, WorkloadMetrics
from models.schemas import WorkloadType, WorkloadPriority, WorkloadStatus

def test_region_model_creation(db_session):
    """Test Region model creation and basic operations"""
    region = Region(
        region_id="test-region-1",
        name="Test Region 1",
        green_energy_score=75.0,
        renewable_percentage=65.0,
        carbon_intensity=200.0,
        electricity_cost=0.12,
        gpu_availability={"A100": 5, "V100": 10},
        cpu_availability=50,
        memory_availability_gb=250.0
    )
    
    db_session.add(region)
    db_session.commit()
    
    # Verify the region was created
    saved_region = db_session.query(Region).filter(Region.region_id == "test-region-1").first()
    assert saved_region is not None
    assert saved_region.name == "Test Region 1"
    assert saved_region.green_energy_score == 75.0
    assert saved_region.gpu_availability["A100"] == 5

def test_region_model_defaults(db_session):
    """Test Region model default values"""
    region = Region(
        region_id="test-region-defaults",
        name="Test Region Defaults"
    )
    
    db_session.add(region)
    db_session.commit()
    
    saved_region = db_session.query(Region).filter(Region.region_id == "test-region-defaults").first()
    assert saved_region.green_energy_score == 0.0
    assert saved_region.renewable_percentage == 0.0
    assert saved_region.carbon_intensity == 0.0
    assert saved_region.electricity_cost == 0.0
    assert saved_region.cpu_availability == 0
    assert saved_region.memory_availability_gb == 0.0
    assert saved_region.is_active is True

def test_workload_model_creation(db_session):
    """Test Workload model creation"""
    workload = Workload(
        workload_id="test-workload-1",
        name="Test Workload 1",
        workload_type=WorkloadType.LLM_TRAINING.value,
        priority=WorkloadPriority.HIGH.value,
        status=WorkloadStatus.SCHEDULED.value,
        estimated_duration_hours=3.0,
        gpu_requirements={"V100": 2},
        memory_gb=64,
        cpu_cores=16,
        region_id="test-us-west-1",
        estimated_cost=45.50,
        estimated_emissions=2.3
    )
    
    db_session.add(workload)
    db_session.commit()
    
    saved_workload = db_session.query(Workload).filter(Workload.workload_id == "test-workload-1").first()
    assert saved_workload is not None
    assert saved_workload.name == "Test Workload 1"
    assert saved_workload.workload_type == WorkloadType.LLM_TRAINING.value
    assert saved_workload.priority == WorkloadPriority.HIGH.value
    assert saved_workload.estimated_duration_hours == 3.0
    assert saved_workload.gpu_requirements["V100"] == 2

def test_workload_model_defaults(db_session):
    """Test Workload model default values"""
    workload = Workload(
        workload_id="test-workload-defaults",
        name="Test Workload Defaults",
        workload_type=WorkloadType.LLM_INFERENCE.value,
        estimated_duration_hours=1.0
    )
    
    db_session.add(workload)
    db_session.commit()
    
    saved_workload = db_session.query(Workload).filter(Workload.workload_id == "test-workload-defaults").first()
    assert saved_workload.priority == WorkloadPriority.MEDIUM.value
    assert saved_workload.status == WorkloadStatus.PENDING.value
    assert saved_workload.created_at is not None
    assert saved_workload.updated_at is not None

def test_region_workload_relationship(db_session):
    """Test relationship between Region and Workload models"""
    # Get existing test region
    region = db_session.query(Region).filter(Region.region_id == "test-us-west-1").first()
    
    # Create workload associated with the region
    workload = Workload(
        workload_id="test-workload-relationship",
        name="Test Relationship Workload",
        workload_type=WorkloadType.MODEL_TRAINING.value,
        estimated_duration_hours=2.0,
        region_id=region.region_id
    )
    
    db_session.add(workload)
    db_session.commit()
    
    # Test the relationship
    saved_workload = db_session.query(Workload).filter(Workload.workload_id == "test-workload-relationship").first()
    assert saved_workload.region is not None
    assert saved_workload.region.region_id == region.region_id
    assert saved_workload.region.name == region.name
    
    # Test reverse relationship
    assert len(region.workloads) >= 1
    workload_ids = [w.workload_id for w in region.workloads]
    assert "test-workload-relationship" in workload_ids

def test_energy_data_model(db_session):
    """Test EnergyData model"""
    energy_data = EnergyData(
        region_id="test-us-west-1",
        timestamp=datetime.now(),
        renewable_percentage=80.0,
        carbon_intensity=120.0,
        electricity_cost=0.14,
        solar_generation=500.0,
        wind_generation=300.0,
        hydro_generation=200.0,
        total_demand=1200.0
    )
    
    db_session.add(energy_data)
    db_session.commit()
    
    saved_data = db_session.query(EnergyData).filter(EnergyData.region_id == "test-us-west-1").first()
    assert saved_data is not None
    assert saved_data.renewable_percentage == 80.0
    assert saved_data.solar_generation == 500.0

def test_workload_metrics_model(db_session):
    """Test WorkloadMetrics model"""
    # First create a workload
    workload = Workload(
        workload_id="test-workload-metrics",
        name="Test Metrics Workload",
        workload_type=WorkloadType.BATCH_INFERENCE.value,
        estimated_duration_hours=1.0
    )
    db_session.add(workload)
    db_session.commit()
    
    # Create metrics for the workload
    metrics = WorkloadMetrics(
        workload_id="test-workload-metrics",
        timestamp=datetime.now(),
        cpu_usage_percent=75.5,
        memory_usage_gb=32.0,
        gpu_usage_percent=90.0,
        power_consumption_watts=450.0,
        carbon_emissions_rate=125.0,
        cost_rate=2.50
    )
    
    db_session.add(metrics)
    db_session.commit()
    
    saved_metrics = db_session.query(WorkloadMetrics).filter(WorkloadMetrics.workload_id == "test-workload-metrics").first()
    assert saved_metrics is not None
    assert saved_metrics.cpu_usage_percent == 75.5
    assert saved_metrics.power_consumption_watts == 450.0

def test_region_json_fields(db_session):
    """Test JSON fields in Region model"""
    region = Region(
        region_id="test-json-fields",
        name="Test JSON Fields",
        location={"lat": 40.7128, "lng": -74.0060},
        gpu_availability={"A100": 10, "V100": 20, "T4": 50},
        renewable_sources={"solar": 30.0, "wind": 25.0, "hydro": 15.0},
        network_latency={"us-east-1": 10, "eu-west-1": 80}
    )
    
    db_session.add(region)
    db_session.commit()
    
    saved_region = db_session.query(Region).filter(Region.region_id == "test-json-fields").first()
    assert saved_region.location["lat"] == 40.7128
    assert saved_region.gpu_availability["A100"] == 10
    assert saved_region.renewable_sources["solar"] == 30.0
    assert saved_region.network_latency["us-east-1"] == 10

def test_workload_json_fields(db_session):
    """Test JSON fields in Workload model"""
    workload = Workload(
        workload_id="test-workload-json",
        name="Test JSON Workload",
        workload_type=WorkloadType.FINE_TUNING.value,
        estimated_duration_hours=4.0,
        gpu_requirements={"A100": 2, "V100": 1},
        preferred_regions=["us-west-1", "eu-north-1"]
    )
    
    db_session.add(workload)
    db_session.commit()
    
    saved_workload = db_session.query(Workload).filter(Workload.workload_id == "test-workload-json").first()
    assert saved_workload.gpu_requirements["A100"] == 2
    assert "us-west-1" in saved_workload.preferred_regions
    assert "eu-north-1" in saved_workload.preferred_regions

def test_model_timestamps(db_session):
    """Test automatic timestamp fields"""
    region = Region(
        region_id="test-timestamps",
        name="Test Timestamps"
    )
    
    db_session.add(region)
    db_session.commit()
    
    saved_region = db_session.query(Region).filter(Region.region_id == "test-timestamps").first()
    assert saved_region.created_at is not None
    assert saved_region.updated_at is not None
    
    # Test that updated_at changes on update
    original_updated_at = saved_region.updated_at
    saved_region.name = "Updated Name"
    db_session.commit()
    
    updated_region = db_session.query(Region).filter(Region.region_id == "test-timestamps").first()
    assert updated_region.updated_at > original_updated_at

def test_region_query_active_only(db_session):
    """Test querying only active regions"""
    # Create an inactive region
    inactive_region = Region(
        region_id="test-inactive",
        name="Inactive Region",
        is_active=False
    )
    db_session.add(inactive_region)
    db_session.commit()
    
    # Query only active regions
    active_regions = db_session.query(Region).filter(Region.is_active == True).all()
    region_ids = [r.region_id for r in active_regions]
    
    assert "test-inactive" not in region_ids
    assert "test-us-west-1" in region_ids  # From conftest.py
    assert "test-eu-north-1" in region_ids  # From conftest.py

