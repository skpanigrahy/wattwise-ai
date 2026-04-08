"""
Workload Allocator - Core scheduling logic for green energy optimization
"""

import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from models.database import Region, Workload
from models.schemas import (
    WorkloadScheduleRequest,
    WorkloadScheduleResponse,
    RegionScore,
    WorkloadStatus,
    RegionDetails,
    WorkloadSummary
)

class WorkloadAllocator:
    """
    Core workload allocation engine that optimizes job placement
    based on green energy availability, cost, and resource constraints
    """
    
    def __init__(self):
        self.weight_green_energy = 0.4
        self.weight_cost = 0.3
        self.weight_availability = 0.2
        self.weight_latency = 0.1
    
    async def schedule_workload(
        self, 
        request: WorkloadScheduleRequest, 
        db: Session
    ) -> WorkloadScheduleResponse:
        """
        Schedule a workload based on green energy optimization
        """
        # Get all available regions
        regions = db.query(Region).filter(Region.is_active == True).all()
        
        if not regions:
            raise Exception("No active regions available")
        
        # Calculate scores for each region
        region_scores = []
        for region in regions:
            score = self._calculate_region_score(region, request)
            if score > 0:  # Only consider regions that meet requirements
                region_scores.append((region, score))
        
        if not region_scores:
            raise Exception("No regions meet the workload requirements")
        
        # Sort by score (highest first)
        region_scores.sort(key=lambda x: x[1], reverse=True)
        best_region = region_scores[0][0]
        
        # Create workload record
        workload_id = str(uuid.uuid4())
        estimated_start_time = datetime.now() + timedelta(minutes=5)  # 5 min buffer
        estimated_end_time = estimated_start_time + timedelta(hours=request.estimated_duration_hours)
        
        # Calculate costs and emissions
        estimated_cost = self._calculate_cost(best_region, request)
        estimated_emissions = self._calculate_emissions(best_region, request)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(best_region, request, region_scores)
        
        # Save to database
        workload = Workload(
            workload_id=workload_id,
            name=request.name,
            workload_type=request.workload_type.value,
            priority=request.priority.value,
            status=WorkloadStatus.SCHEDULED.value,
            estimated_duration_hours=request.estimated_duration_hours,
            gpu_requirements=request.gpu_requirements,
            memory_gb=request.memory_gb,
            cpu_cores=request.cpu_cores,
            preferred_regions=request.preferred_regions,
            max_cost_per_hour=request.max_cost_per_hour,
            max_carbon_emissions=request.max_carbon_emissions,
            deadline=request.deadline,
            region_id=best_region.region_id,
            estimated_start_time=estimated_start_time,
            estimated_end_time=estimated_end_time,
            estimated_cost=estimated_cost,
            estimated_emissions=estimated_emissions,
            reasoning=reasoning
        )
        
        db.add(workload)
        db.commit()
        db.refresh(workload)
        
        return WorkloadScheduleResponse(
            workload_id=workload_id,
            status=WorkloadStatus.SCHEDULED,
            recommended_region=best_region.region_id,
            estimated_start_time=estimated_start_time,
            estimated_end_time=estimated_end_time,
            estimated_cost=estimated_cost,
            estimated_emissions=estimated_emissions,
            green_energy_score=best_region.green_energy_score,
            reasoning=reasoning
        )
    
    def _calculate_region_score(self, region: Region, request: WorkloadScheduleRequest) -> float:
        """
        Calculate a composite score for a region based on multiple factors
        """
        # Check hard constraints first
        if not self._meets_requirements(region, request):
            return 0.0
        
        # Green energy score (0-100, normalize to 0-1)
        green_score = region.green_energy_score / 100.0
        
        # Cost score (lower cost = higher score)
        cost_score = max(0, 1 - (region.electricity_cost / 0.25))  # Normalize against $0.25/kWh
        
        # Availability score (based on GPU availability)
        availability_score = self._calculate_availability_score(region, request)
        
        # Latency score (placeholder - could be enhanced with actual latency data)
        latency_score = 0.8  # Default good latency
        
        # Weighted composite score
        composite_score = (
            self.weight_green_energy * green_score +
            self.weight_cost * cost_score +
            self.weight_availability * availability_score +
            self.weight_latency * latency_score
        )
        
        return composite_score
    
    def _meets_requirements(self, region: Region, request: WorkloadScheduleRequest) -> bool:
        """
        Check if region meets hard requirements
        """
        # Check preferred regions
        if request.preferred_regions and region.region_id not in request.preferred_regions:
            return False
        
        # Check GPU requirements
        if request.gpu_requirements:
            for gpu_type, required_count in request.gpu_requirements.items():
                available = region.gpu_availability.get(gpu_type, 0)
                if available < required_count:
                    return False
        
        # Check memory requirements
        if request.memory_gb and region.memory_availability_gb < request.memory_gb:
            return False
        
        # Check CPU requirements
        if request.cpu_cores and region.cpu_availability < request.cpu_cores:
            return False
        
        # Check cost constraints
        if request.max_cost_per_hour:
            estimated_hourly_cost = self._calculate_hourly_cost(region, request)
            if estimated_hourly_cost > request.max_cost_per_hour:
                return False
        
        # Check emissions constraints
        if request.max_carbon_emissions:
            estimated_emissions = self._calculate_emissions(region, request)
            if estimated_emissions > request.max_carbon_emissions:
                return False
        
        return True
    
    def _calculate_availability_score(self, region: Region, request: WorkloadScheduleRequest) -> float:
        """
        Calculate availability score based on resource availability
        """
        if not request.gpu_requirements:
            return 1.0
        
        total_score = 0.0
        total_weight = 0.0
        
        for gpu_type, required_count in request.gpu_requirements.items():
            available = region.gpu_availability.get(gpu_type, 0)
            if available > 0:
                # Score based on availability ratio (capped at 1.0)
                score = min(1.0, available / (required_count * 2))  # 2x buffer for good score
                total_score += score * required_count
                total_weight += required_count
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _calculate_cost(self, region: Region, request: WorkloadScheduleRequest) -> float:
        """
        Calculate estimated total cost for the workload
        """
        hourly_cost = self._calculate_hourly_cost(region, request)
        return hourly_cost * request.estimated_duration_hours
    
    def _calculate_hourly_cost(self, region: Region, request: WorkloadScheduleRequest) -> float:
        """
        Calculate estimated hourly cost
        """
        # Base electricity cost
        base_cost = region.electricity_cost
        
        # GPU cost multiplier (simplified)
        gpu_multiplier = 1.0
        if request.gpu_requirements:
            for gpu_type, count in request.gpu_requirements.items():
                if gpu_type == "A100":
                    gpu_multiplier += count * 3.0
                elif gpu_type == "V100":
                    gpu_multiplier += count * 2.0
                elif gpu_type == "T4":
                    gpu_multiplier += count * 1.0
        
        # Memory cost
        memory_cost = (request.memory_gb or 0) * 0.001  # $0.001 per GB per hour
        
        # CPU cost
        cpu_cost = (request.cpu_cores or 0) * 0.05  # $0.05 per core per hour
        
        return base_cost * gpu_multiplier + memory_cost + cpu_cost
    
    def _calculate_emissions(self, region: Region, request: WorkloadScheduleRequest) -> float:
        """
        Calculate estimated carbon emissions in kg CO2
        """
        # Estimated power consumption (simplified)
        base_power = 100  # 100W base
        
        if request.gpu_requirements:
            for gpu_type, count in request.gpu_requirements.items():
                if gpu_type == "A100":
                    base_power += count * 400  # 400W per A100
                elif gpu_type == "V100":
                    base_power += count * 300  # 300W per V100
                elif gpu_type == "T4":
                    base_power += count * 70   # 70W per T4
        
        # Total energy consumption in kWh
        total_energy_kwh = (base_power / 1000) * request.estimated_duration_hours
        
        # Carbon emissions = energy * carbon intensity
        emissions_kg = total_energy_kwh * (region.carbon_intensity / 1000)  # Convert g to kg
        
        return emissions_kg
    
    def _generate_reasoning(
        self, 
        selected_region: Region, 
        request: WorkloadScheduleRequest,
        all_scores: List[tuple]
    ) -> str:
        """
        Generate human-readable reasoning for the region selection
        """
        reasoning_parts = [
            f"Selected {selected_region.name} for optimal green energy utilization."
        ]
        
        # Green energy highlights
        if selected_region.green_energy_score >= 80:
            reasoning_parts.append(
                f"Excellent green energy score of {selected_region.green_energy_score:.1f}% "
                f"with {selected_region.renewable_percentage:.1f}% renewable energy."
            )
        elif selected_region.green_energy_score >= 60:
            reasoning_parts.append(
                f"Good green energy score of {selected_region.green_energy_score:.1f}% "
                f"with {selected_region.renewable_percentage:.1f}% renewable energy."
            )
        
        # Cost considerations
        if selected_region.electricity_cost <= 0.12:
            reasoning_parts.append(f"Low electricity cost of ${selected_region.electricity_cost:.3f}/kWh.")
        
        # Emissions
        if selected_region.carbon_intensity <= 150:
            reasoning_parts.append(f"Low carbon intensity of {selected_region.carbon_intensity:.0f} gCO2/kWh.")
        
        # Resource availability
        if request.gpu_requirements:
            gpu_info = []
            for gpu_type, count in request.gpu_requirements.items():
                available = selected_region.gpu_availability.get(gpu_type, 0)
                gpu_info.append(f"{available} {gpu_type} GPUs available")
            reasoning_parts.append(f"Sufficient resources: {', '.join(gpu_info)}.")
        
        return " ".join(reasoning_parts)
    
    async def get_region_scores(self, db: Session) -> List[RegionScore]:
        """
        Get current green energy scores for all regions
        """
        regions = db.query(Region).filter(Region.is_active == True).all()
        
        scores = []
        for region in regions:
            score = RegionScore(
                region_id=region.region_id,
                region_name=region.name,
                green_energy_score=region.green_energy_score,
                renewable_percentage=region.renewable_percentage,
                carbon_intensity=region.carbon_intensity,
                electricity_cost=region.electricity_cost,
                gpu_availability=region.gpu_availability,
                cpu_availability=region.cpu_availability,
                memory_availability_gb=region.memory_availability_gb,
                last_updated=region.updated_at
            )
            scores.append(score)
        
        return scores
    
    async def get_region_details(self, region_id: str, db: Session) -> Optional[RegionDetails]:
        """
        Get detailed information about a specific region
        """
        region = db.query(Region).filter(Region.region_id == region_id).first()
        
        if not region:
            return None
        
        # Convert GPU availability to detailed format
        gpu_types = []
        for gpu_type, count in region.gpu_availability.items():
            gpu_types.append({
                "type": gpu_type,
                "available_count": count,
                "specifications": self._get_gpu_specs(gpu_type)
            })
        
        return RegionDetails(
            region_id=region.region_id,
            region_name=region.name,
            location=region.location or {},
            green_energy_score=region.green_energy_score,
            renewable_sources=region.renewable_sources or {},
            carbon_intensity=region.carbon_intensity,
            electricity_cost=region.electricity_cost,
            gpu_types=gpu_types,
            network_latency=region.network_latency or {},
            weather_forecast=region.weather_forecast
        )
    
    def _get_gpu_specs(self, gpu_type: str) -> Dict[str, Any]:
        """
        Get GPU specifications (simplified)
        """
        specs = {
            "A100": {"memory_gb": 40, "compute_capability": "8.0", "power_watts": 400},
            "V100": {"memory_gb": 16, "compute_capability": "7.0", "power_watts": 300},
            "T4": {"memory_gb": 16, "compute_capability": "7.5", "power_watts": 70}
        }
        return specs.get(gpu_type, {})
    
    async def get_workloads(
        self, 
        status: Optional[str] = None,
        region_id: Optional[str] = None,
        db: Session = None
    ) -> List[WorkloadSummary]:
        """
        Get list of workloads with optional filtering
        """
        query = db.query(Workload)
        
        if status:
            query = query.filter(Workload.status == status)
        
        if region_id:
            query = query.filter(Workload.region_id == region_id)
        
        workloads = query.order_by(Workload.created_at.desc()).all()
        
        summaries = []
        for workload in workloads:
            summary = WorkloadSummary(
                workload_id=workload.workload_id,
                name=workload.name,
                workload_type=workload.workload_type,
                status=workload.status,
                region_id=workload.region_id,
                start_time=workload.actual_start_time,
                end_time=workload.actual_end_time,
                estimated_cost=workload.estimated_cost,
                actual_cost=workload.actual_cost,
                estimated_emissions=workload.estimated_emissions,
                actual_emissions=workload.actual_emissions,
                created_at=workload.created_at
            )
            summaries.append(summary)
        
        return summaries

