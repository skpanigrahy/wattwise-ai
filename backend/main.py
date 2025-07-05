"""
WattWise AI - Smart AI Workload Scheduler
Main FastAPI application
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import uvicorn
import os
from typing import List, Dict, Any
from datetime import datetime

from models.schemas import (
    WorkloadScheduleRequest,
    WorkloadScheduleResponse,
    RegionScore,
    AgentQueryRequest,
    AgentQueryResponse
)
from scheduler.allocator import WorkloadAllocator
from agent.assistant import GreenComputeAssistant
from db.session import get_db, SessionLocal

# Prometheus metrics
REQUEST_COUNT = Counter('wattwise_requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('wattwise_request_duration_seconds', 'Request duration')

app = FastAPI(
    title="WattWise AI",
    description="Smart AI Workload Scheduler for Green Energy Optimization",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
allocator = WorkloadAllocator()
assistant = GreenComputeAssistant()

@app.middleware("http")
async def prometheus_middleware(request, call_next):
    """Middleware to collect Prometheus metrics"""
    start_time = datetime.now()
    
    response = await call_next(request)
    
    # Record metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path
    ).inc()
    
    duration = (datetime.now() - start_time).total_seconds()
    REQUEST_DURATION.observe(duration)
    
    return response

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to WattWise AI - Smart AI Workload Scheduler",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/jobs/schedule", response_model=WorkloadScheduleResponse)
async def schedule_workload(
    request: WorkloadScheduleRequest,
    db: SessionLocal = Depends(get_db)
):
    """
    Schedule a new AI workload based on green energy availability
    """
    try:
        result = await allocator.schedule_workload(request, db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/regions/scores", response_model=List[RegionScore])
async def get_region_scores(db: SessionLocal = Depends(get_db)):
    """
    Get green energy scores for all regions
    """
    try:
        scores = await allocator.get_region_scores(db)
        return scores
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/query", response_model=AgentQueryResponse)
async def query_agent(request: AgentQueryRequest):
    """
    Query the LangChain assistant for green compute recommendations
    """
    try:
        response = await assistant.query(request.query)
        return AgentQueryResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint
    """
    return PlainTextResponse(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

@app.get("/regions/{region_id}/details")
async def get_region_details(region_id: str, db: SessionLocal = Depends(get_db)):
    """
    Get detailed information about a specific region
    """
    try:
        details = await allocator.get_region_details(region_id, db)
        if not details:
            raise HTTPException(status_code=404, detail="Region not found")
        return details
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/workloads")
async def get_workloads(
    status: str = None,
    region_id: str = None,
    db: SessionLocal = Depends(get_db)
):
    """
    Get list of workloads with optional filtering
    """
    try:
        workloads = await allocator.get_workloads(status=status, region_id=region_id, db=db)
        return workloads
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )

