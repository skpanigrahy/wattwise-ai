"""
Additional monitoring metrics for WattWise AI
"""

from prometheus_client import Counter, Histogram, Gauge, Info
import time
from functools import wraps

# Application metrics
WORKLOAD_SCHEDULED_TOTAL = Counter(
    'wattwise_workloads_scheduled_total',
    'Total number of workloads scheduled',
    ['region', 'workload_type', 'priority']
)

WORKLOAD_DURATION = Histogram(
    'wattwise_workload_duration_hours',
    'Duration of workloads in hours',
    ['region', 'workload_type']
)

REGION_GREEN_SCORE = Gauge(
    'wattwise_region_green_energy_score',
    'Green energy score by region',
    ['region_id', 'region_name']
)

REGION_CARBON_INTENSITY = Gauge(
    'wattwise_region_carbon_intensity_gco2_kwh',
    'Carbon intensity by region in gCO2/kWh',
    ['region_id', 'region_name']
)

REGION_ELECTRICITY_COST = Gauge(
    'wattwise_region_electricity_cost_per_kwh',
    'Electricity cost by region per kWh',
    ['region_id', 'region_name']
)

REGION_GPU_AVAILABILITY = Gauge(
    'wattwise_region_gpu_availability',
    'GPU availability by region and type',
    ['region_id', 'region_name', 'gpu_type']
)

ACTIVE_WORKLOADS = Gauge(
    'wattwise_active_workloads',
    'Number of active workloads',
    ['status', 'region']
)

ASSISTANT_QUERIES_TOTAL = Counter(
    'wattwise_assistant_queries_total',
    'Total number of assistant queries',
    ['query_type']
)

ASSISTANT_RESPONSE_TIME = Histogram(
    'wattwise_assistant_response_time_seconds',
    'Assistant response time in seconds'
)

# Application info
APP_INFO = Info(
    'wattwise_app_info',
    'WattWise AI application information'
)

# Set application info
APP_INFO.info({
    'version': '1.0.0',
    'name': 'WattWise AI',
    'description': 'Smart AI Workload Scheduler for Green Energy Optimization'
})

def track_workload_scheduled(region_id, workload_type, priority):
    """Track when a workload is scheduled"""
    WORKLOAD_SCHEDULED_TOTAL.labels(
        region=region_id,
        workload_type=workload_type,
        priority=priority
    ).inc()

def track_workload_duration(region_id, workload_type, duration_hours):
    """Track workload duration"""
    WORKLOAD_DURATION.labels(
        region=region_id,
        workload_type=workload_type
    ).observe(duration_hours)

def update_region_metrics(regions):
    """Update region-related metrics"""
    for region in regions:
        # Green energy score
        REGION_GREEN_SCORE.labels(
            region_id=region.region_id,
            region_name=region.name
        ).set(region.green_energy_score)
        
        # Carbon intensity
        REGION_CARBON_INTENSITY.labels(
            region_id=region.region_id,
            region_name=region.name
        ).set(region.carbon_intensity)
        
        # Electricity cost
        REGION_ELECTRICITY_COST.labels(
            region_id=region.region_id,
            region_name=region.name
        ).set(region.electricity_cost)
        
        # GPU availability
        for gpu_type, count in region.gpu_availability.items():
            REGION_GPU_AVAILABILITY.labels(
                region_id=region.region_id,
                region_name=region.name,
                gpu_type=gpu_type
            ).set(count)

def update_workload_metrics(workloads):
    """Update workload-related metrics"""
    # Reset gauges
    ACTIVE_WORKLOADS._metrics.clear()
    
    # Count workloads by status and region
    status_counts = {}
    for workload in workloads:
        key = (workload.status, workload.region_id or 'unassigned')
        status_counts[key] = status_counts.get(key, 0) + 1
    
    # Set gauge values
    for (status, region), count in status_counts.items():
        ACTIVE_WORKLOADS.labels(status=status, region=region).set(count)

def track_assistant_query(query_type="general"):
    """Track assistant query"""
    ASSISTANT_QUERIES_TOTAL.labels(query_type=query_type).inc()

def track_assistant_response_time(func):
    """Decorator to track assistant response time"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            duration = time.time() - start_time
            ASSISTANT_RESPONSE_TIME.observe(duration)
    return wrapper

