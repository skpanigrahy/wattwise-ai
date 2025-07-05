"""
Tests for WattWise AI scheduling logic
"""

import pytest
from datetime import datetime
from models.schemas import WorkloadScheduleRequest, WorkloadType, WorkloadPriority
from scheduler.allocator import WorkloadAllocator
from models.database import Region

@pytest.fixture
def allocator():
    """Create WorkloadAllocator instance"""
    return WorkloadAllocator()

@pytest.fixture
def sample_request():
    """Sample workload request"""
    return WorkloadScheduleRequest(
        name="Test Workload",
        workload_type=WorkloadType.LLM_TRAINING,
        priority=WorkloadPriority.MEDIUM,
        estimated_duration_hours=2.0,
        gpu_requirements={"V100": 1},
        memory_gb=16,
        cpu_cores=4,
        max_cost_per_hour=15.0,
        max_carbon_emissions=5.0
    )

def test_calculate_region_score(allocator, db_session, sample_request):
    """Test region scoring calculation"""
    # Get a test region
    region = db_session.query(Region).filter(Region.region_id == "test-us-west-1").first()
    
    score = allocator._calculate_region_score(region, sample_request)
    assert 0 <= score <= 1  # Score should be normalized between 0 and 1
    assert score > 0  # Should meet requirements

def test_meets_requirements_gpu(allocator, db_session):
    """Test GPU requirements checking"""
    region = db_session.query(Region).filter(Region.region_id == "test-us-west-1").first()
    
    # Request that should pass
    request_pass = WorkloadScheduleRequest(
        name="Test",
        workload_type=WorkloadType.LLM_TRAINING,
        estimated_duration_hours=1.0,
        gpu_requirements={"V100": 1}  # Region has 20 V100s
    )
    assert allocator._meets_requirements(region, request_pass)
    
    # Request that should fail
    request_fail = WorkloadScheduleRequest(
        name="Test",
        workload_type=WorkloadType.LLM_TRAINING,
        estimated_duration_hours=1.0,
        gpu_requirements={"V100": 100}  # Region only has 20 V100s
    )
    assert not allocator._meets_requirements(region, request_fail)

def test_meets_requirements_memory(allocator, db_session):
    """Test memory requirements checking"""
    region = db_session.query(Region).filter(Region.region_id == "test-us-west-1").first()
    
    # Request that should pass
    request_pass = WorkloadScheduleRequest(
        name="Test",
        workload_type=WorkloadType.LLM_TRAINING,
        estimated_duration_hours=1.0,
        memory_gb=100  # Region has 500GB
    )
    assert allocator._meets_requirements(region, request_pass)
    
    # Request that should fail
    request_fail = WorkloadScheduleRequest(
        name="Test",
        workload_type=WorkloadType.LLM_TRAINING,
        estimated_duration_hours=1.0,
        memory_gb=1000  # Region only has 500GB
    )
    assert not allocator._meets_requirements(region, request_fail)

def test_meets_requirements_cost(allocator, db_session):
    """Test cost requirements checking"""
    region = db_session.query(Region).filter(Region.region_id == "test-us-west-1").first()
    
    # Request with reasonable cost limit
    request_pass = WorkloadScheduleRequest(
        name="Test",
        workload_type=WorkloadType.LLM_TRAINING,
        estimated_duration_hours=1.0,
        max_cost_per_hour=50.0  # High limit
    )
    assert allocator._meets_requirements(region, request_pass)
    
    # Request with very low cost limit
    request_fail = WorkloadScheduleRequest(
        name="Test",
        workload_type=WorkloadType.LLM_TRAINING,
        estimated_duration_hours=1.0,
        gpu_requirements={"A100": 5},  # Expensive GPUs
        max_cost_per_hour=0.01  # Very low limit
    )
    assert not allocator._meets_requirements(region, request_fail)

def test_calculate_cost(allocator, db_session, sample_request):
    """Test cost calculation"""
    region = db_session.query(Region).filter(Region.region_id == "test-us-west-1").first()
    
    cost = allocator._calculate_cost(region, sample_request)
    assert cost > 0
    assert isinstance(cost, float)
    
    # Cost should scale with duration
    longer_request = WorkloadScheduleRequest(
        name="Test",
        workload_type=WorkloadType.LLM_TRAINING,
        estimated_duration_hours=4.0,  # Double duration
        gpu_requirements={"V100": 1},
        memory_gb=16,
        cpu_cores=4
    )
    longer_cost = allocator._calculate_cost(region, longer_request)
    assert longer_cost > cost

def test_calculate_emissions(allocator, db_session, sample_request):
    """Test emissions calculation"""
    region = db_session.query(Region).filter(Region.region_id == "test-us-west-1").first()
    
    emissions = allocator._calculate_emissions(region, sample_request)
    assert emissions > 0
    assert isinstance(emissions, float)
    
    # Emissions should be lower for regions with lower carbon intensity
    low_carbon_region = db_session.query(Region).filter(Region.region_id == "test-eu-north-1").first()
    low_emissions = allocator._calculate_emissions(low_carbon_region, sample_request)
    assert low_emissions < emissions  # EU North has lower carbon intensity

@pytest.mark.asyncio
async def test_schedule_workload(allocator, db_session, sample_request):
    """Test complete workload scheduling"""
    result = await allocator.schedule_workload(sample_request, db_session)
    
    assert result.workload_id is not None
    assert result.status.value == "scheduled"
    assert result.recommended_region in ["test-us-west-1", "test-eu-north-1"]
    assert result.estimated_cost > 0
    assert result.estimated_emissions > 0
    assert len(result.reasoning) > 0

@pytest.mark.asyncio
async def test_schedule_workload_prefers_green_energy(allocator, db_session):
    """Test that scheduler prefers regions with higher green energy scores"""
    # Request that both regions can handle
    request = WorkloadScheduleRequest(
        name="Green Test",
        workload_type=WorkloadType.LLM_INFERENCE,
        estimated_duration_hours=1.0,
        gpu_requirements={"T4": 1},  # Both regions have T4s
        memory_gb=8,
        cpu_cores=2
    )
    
    result = await allocator.schedule_workload(request, db_session)
    
    # Should prefer EU North (95% green) over US West (85% green)
    assert result.recommended_region == "test-eu-north-1"

@pytest.mark.asyncio
async def test_get_region_scores(allocator, db_session):
    """Test getting region scores"""
    scores = await allocator.get_region_scores(db_session)
    
    assert len(scores) == 2  # We have 2 test regions
    assert all(hasattr(score, 'region_id') for score in scores)
    assert all(hasattr(score, 'green_energy_score') for score in scores)
    assert all(0 <= score.green_energy_score <= 100 for score in scores)

@pytest.mark.asyncio
async def test_get_region_details(allocator, db_session):
    """Test getting region details"""
    details = await allocator.get_region_details("test-us-west-1", db_session)
    
    assert details is not None
    assert details.region_id == "test-us-west-1"
    assert details.region_name == "Test US West"
    assert len(details.gpu_types) > 0
    
    # Test non-existent region
    none_details = await allocator.get_region_details("non-existent", db_session)
    assert none_details is None

def test_availability_score_calculation(allocator, db_session):
    """Test GPU availability score calculation"""
    region = db_session.query(Region).filter(Region.region_id == "test-us-west-1").first()
    
    # Request with available GPUs
    request_available = WorkloadScheduleRequest(
        name="Test",
        workload_type=WorkloadType.LLM_TRAINING,
        estimated_duration_hours=1.0,
        gpu_requirements={"V100": 1}  # Region has 20
    )
    score_available = allocator._calculate_availability_score(region, request_available)
    assert score_available > 0
    
    # Request with no GPU requirements
    request_no_gpu = WorkloadScheduleRequest(
        name="Test",
        workload_type=WorkloadType.LLM_TRAINING,
        estimated_duration_hours=1.0
    )
    score_no_gpu = allocator._calculate_availability_score(region, request_no_gpu)
    assert score_no_gpu == 1.0  # Should be perfect score

def test_generate_reasoning(allocator, db_session, sample_request):
    """Test reasoning generation"""
    region = db_session.query(Region).filter(Region.region_id == "test-eu-north-1").first()
    
    reasoning = allocator._generate_reasoning(region, sample_request, [(region, 0.9)])
    
    assert isinstance(reasoning, str)
    assert len(reasoning) > 0
    assert region.name in reasoning
    assert "green energy" in reasoning.lower() or "renewable" in reasoning.lower()

