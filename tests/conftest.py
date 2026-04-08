"""
Test configuration and fixtures for WattWise AI
"""

import pytest
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from models.database import Base, Region, Workload
from db.session import get_db
from main import app

# Test database URL
TEST_DATABASE_URL = "sqlite:///./test_wattwise.db"

@pytest.fixture(scope="session")
def engine():
    """Create test database engine"""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(engine):
    """Create test database session"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    
    # Create sample test data
    test_regions = [
        Region(
            region_id="test-us-west-1",
            name="Test US West",
            green_energy_score=85.0,
            renewable_percentage=75.0,
            carbon_intensity=150.0,
            electricity_cost=0.15,
            gpu_availability={"A100": 10, "V100": 20, "T4": 50},
            cpu_availability=100,
            memory_availability_gb=500.0,
            renewable_sources={"solar": 45.0, "wind": 20.0, "hydro": 10.0}
        ),
        Region(
            region_id="test-eu-north-1",
            name="Test EU North",
            green_energy_score=95.0,
            renewable_percentage=90.0,
            carbon_intensity=80.0,
            electricity_cost=0.10,
            gpu_availability={"A100": 5, "V100": 15, "T4": 30},
            cpu_availability=80,
            memory_availability_gb=400.0,
            renewable_sources={"hydro": 45.0, "wind": 35.0, "solar": 10.0}
        )
    ]
    
    for region in test_regions:
        session.add(region)
    session.commit()
    
    yield session
    session.close()

@pytest.fixture
def client(db_session):
    """Create test client with database override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture
def sample_workload_request():
    """Sample workload request for testing"""
    return {
        "name": "Test LLM Training",
        "workload_type": "llm_training",
        "priority": "medium",
        "estimated_duration_hours": 2.0,
        "gpu_requirements": {"V100": 2},
        "memory_gb": 32,
        "cpu_cores": 8,
        "max_cost_per_hour": 20.0,
        "max_carbon_emissions": 10.0
    }

