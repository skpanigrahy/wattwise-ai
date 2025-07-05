"""
Pydantic schemas for API requests and responses
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class WorkloadType(str, Enum):
    """Types of AI workloads"""
    LLM_TRAINING = "llm_training"
    LLM_INFERENCE = "llm_inference"
    MODEL_TRAINING = "model_training"
    BATCH_INFERENCE = "batch_inference"
    FINE_TUNING = "fine_tuning"

class WorkloadPriority(str, Enum):
    """Workload priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class WorkloadStatus(str, Enum):
    """Workload status"""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class WorkloadScheduleRequest(BaseModel):
    """Request to schedule a new workload"""
    name: str = Field(..., description="Name of the workload")
    workload_type: WorkloadType = Field(..., description="Type of AI workload")
    priority: WorkloadPriority = Field(default=WorkloadPriority.MEDIUM, description="Priority level")
    estimated_duration_hours: float = Field(..., gt=0, description="Estimated duration in hours")
    gpu_requirements: Dict[str, Any] = Field(default_factory=dict, description="GPU requirements")
    memory_gb: Optional[float] = Field(None, gt=0, description="Memory requirements in GB")
    cpu_cores: Optional[int] = Field(None, gt=0, description="CPU core requirements")
    preferred_regions: Optional[List[str]] = Field(default=None, description="Preferred regions")
    max_cost_per_hour: Optional[float] = Field(None, gt=0, description="Maximum cost per hour")
    max_carbon_emissions: Optional[float] = Field(None, gt=0, description="Maximum carbon emissions")
    deadline: Optional[datetime] = Field(None, description="Deadline for completion")

class WorkloadScheduleResponse(BaseModel):
    """Response for workload scheduling"""
    workload_id: str = Field(..., description="Unique workload identifier")
    status: WorkloadStatus = Field(..., description="Current status")
    recommended_region: str = Field(..., description="Recommended region for execution")
    estimated_start_time: datetime = Field(..., description="Estimated start time")
    estimated_end_time: datetime = Field(..., description="Estimated end time")
    estimated_cost: float = Field(..., description="Estimated total cost")
    estimated_emissions: float = Field(..., description="Estimated carbon emissions")
    green_energy_score: float = Field(..., description="Green energy score of recommended region")
    reasoning: str = Field(..., description="Reasoning for the recommendation")

class RegionScore(BaseModel):
    """Green energy score for a region"""
    region_id: str = Field(..., description="Region identifier")
    region_name: str = Field(..., description="Human-readable region name")
    green_energy_score: float = Field(..., ge=0, le=100, description="Green energy score (0-100)")
    renewable_percentage: float = Field(..., ge=0, le=100, description="Renewable energy percentage")
    carbon_intensity: float = Field(..., ge=0, description="Carbon intensity (gCO2/kWh)")
    electricity_cost: float = Field(..., ge=0, description="Electricity cost per kWh")
    gpu_availability: Dict[str, int] = Field(default_factory=dict, description="Available GPU types and counts")
    cpu_availability: int = Field(..., ge=0, description="Available CPU cores")
    memory_availability_gb: float = Field(..., ge=0, description="Available memory in GB")
    last_updated: datetime = Field(..., description="Last update timestamp")

class AgentQueryRequest(BaseModel):
    """Request to query the AI assistant"""
    query: str = Field(..., min_length=1, description="Query for the assistant")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")

class AgentQueryResponse(BaseModel):
    """Response from the AI assistant"""
    response: str = Field(..., description="Assistant's response")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    sources: Optional[List[str]] = Field(default=None, description="Sources used for the response")

class RegionDetails(BaseModel):
    """Detailed information about a region"""
    region_id: str = Field(..., description="Region identifier")
    region_name: str = Field(..., description="Human-readable region name")
    location: Dict[str, float] = Field(..., description="Geographic coordinates")
    green_energy_score: float = Field(..., ge=0, le=100, description="Green energy score")
    renewable_sources: Dict[str, float] = Field(..., description="Breakdown of renewable sources")
    carbon_intensity: float = Field(..., description="Carbon intensity")
    electricity_cost: float = Field(..., description="Electricity cost")
    gpu_types: List[Dict[str, Any]] = Field(..., description="Available GPU types and specifications")
    network_latency: Dict[str, float] = Field(..., description="Network latency to other regions")
    weather_forecast: Optional[Dict[str, Any]] = Field(None, description="Weather forecast affecting renewable energy")

class WorkloadSummary(BaseModel):
    """Summary of a workload"""
    workload_id: str = Field(..., description="Workload identifier")
    name: str = Field(..., description="Workload name")
    workload_type: WorkloadType = Field(..., description="Type of workload")
    status: WorkloadStatus = Field(..., description="Current status")
    region_id: Optional[str] = Field(None, description="Assigned region")
    start_time: Optional[datetime] = Field(None, description="Actual start time")
    end_time: Optional[datetime] = Field(None, description="Actual end time")
    estimated_cost: Optional[float] = Field(None, description="Estimated cost")
    actual_cost: Optional[float] = Field(None, description="Actual cost")
    estimated_emissions: Optional[float] = Field(None, description="Estimated emissions")
    actual_emissions: Optional[float] = Field(None, description="Actual emissions")
    created_at: datetime = Field(..., description="Creation timestamp")

