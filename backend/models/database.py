"""
SQLAlchemy database models
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

Base = declarative_base()

class Region(Base):
    """Region model for storing region information"""
    __tablename__ = "regions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    region_id = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    location = Column(JSON, nullable=True)  # {"lat": float, "lng": float}
    green_energy_score = Column(Float, nullable=False, default=0.0)
    renewable_percentage = Column(Float, nullable=False, default=0.0)
    carbon_intensity = Column(Float, nullable=False, default=0.0)  # gCO2/kWh
    electricity_cost = Column(Float, nullable=False, default=0.0)  # per kWh
    gpu_availability = Column(JSON, nullable=True, default=dict)  # {"gpu_type": count}
    cpu_availability = Column(Integer, nullable=False, default=0)
    memory_availability_gb = Column(Float, nullable=False, default=0.0)
    renewable_sources = Column(JSON, nullable=True, default=dict)  # {"solar": %, "wind": %}
    network_latency = Column(JSON, nullable=True, default=dict)  # {"region_id": latency_ms}
    weather_forecast = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    workloads = relationship("Workload", back_populates="region")

class Workload(Base):
    """Workload model for storing AI workload information"""
    __tablename__ = "workloads"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workload_id = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    workload_type = Column(String, nullable=False)  # WorkloadType enum
    priority = Column(String, nullable=False, default="medium")  # WorkloadPriority enum
    status = Column(String, nullable=False, default="pending")  # WorkloadStatus enum
    
    # Requirements
    estimated_duration_hours = Column(Float, nullable=False)
    gpu_requirements = Column(JSON, nullable=True, default=dict)
    memory_gb = Column(Float, nullable=True)
    cpu_cores = Column(Integer, nullable=True)
    preferred_regions = Column(JSON, nullable=True)  # List of region IDs
    max_cost_per_hour = Column(Float, nullable=True)
    max_carbon_emissions = Column(Float, nullable=True)
    deadline = Column(DateTime, nullable=True)
    
    # Assignment
    region_id = Column(String, ForeignKey("regions.region_id"), nullable=True)
    
    # Scheduling
    estimated_start_time = Column(DateTime, nullable=True)
    estimated_end_time = Column(DateTime, nullable=True)
    actual_start_time = Column(DateTime, nullable=True)
    actual_end_time = Column(DateTime, nullable=True)
    
    # Costs and emissions
    estimated_cost = Column(Float, nullable=True)
    actual_cost = Column(Float, nullable=True)
    estimated_emissions = Column(Float, nullable=True)  # kg CO2
    actual_emissions = Column(Float, nullable=True)  # kg CO2
    
    # Metadata
    reasoning = Column(Text, nullable=True)  # Reasoning for region selection
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    region = relationship("Region", back_populates="workloads")

class EnergyData(Base):
    """Historical energy data for regions"""
    __tablename__ = "energy_data"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    region_id = Column(String, ForeignKey("regions.region_id"), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    renewable_percentage = Column(Float, nullable=False)
    carbon_intensity = Column(Float, nullable=False)
    electricity_cost = Column(Float, nullable=False)
    solar_generation = Column(Float, nullable=True)  # MW
    wind_generation = Column(Float, nullable=True)  # MW
    hydro_generation = Column(Float, nullable=True)  # MW
    total_demand = Column(Float, nullable=True)  # MW
    weather_conditions = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=func.now())

class WorkloadMetrics(Base):
    """Metrics for workload execution"""
    __tablename__ = "workload_metrics"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workload_id = Column(String, ForeignKey("workloads.workload_id"), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    cpu_usage_percent = Column(Float, nullable=True)
    memory_usage_gb = Column(Float, nullable=True)
    gpu_usage_percent = Column(Float, nullable=True)
    power_consumption_watts = Column(Float, nullable=True)
    carbon_emissions_rate = Column(Float, nullable=True)  # gCO2/hour
    cost_rate = Column(Float, nullable=True)  # cost/hour
    created_at = Column(DateTime, default=func.now())

