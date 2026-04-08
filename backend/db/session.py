"""
Database session management
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from models.database import Base
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://wattwise:wattwise123@localhost:5432/wattwise_db"
)

# For testing, use SQLite
if os.getenv("TESTING"):
    DATABASE_URL = "sqlite:///./test_wattwise.db"

# Create engine
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def get_db() -> Session:
    """
    Dependency to get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database with sample data"""
    create_tables()
    
    db = SessionLocal()
    try:
        # Import here to avoid circular imports
        from models.database import Region
        
        # Check if regions already exist
        existing_regions = db.query(Region).count()
        if existing_regions > 0:
            return
        
        # Sample regions with green energy data
        sample_regions = [
            {
                "region_id": "us-west-1",
                "name": "US West (California)",
                "location": {"lat": 37.7749, "lng": -122.4194},
                "green_energy_score": 85.0,
                "renewable_percentage": 75.0,
                "carbon_intensity": 150.0,
                "electricity_cost": 0.15,
                "gpu_availability": {"A100": 50, "V100": 100, "T4": 200},
                "cpu_availability": 1000,
                "memory_availability_gb": 5000.0,
                "renewable_sources": {"solar": 45.0, "wind": 20.0, "hydro": 10.0},
                "network_latency": {"us-east-1": 70, "eu-west-1": 150}
            },
            {
                "region_id": "us-east-1",
                "name": "US East (Virginia)",
                "location": {"lat": 38.9072, "lng": -77.0369},
                "green_energy_score": 65.0,
                "renewable_percentage": 55.0,
                "carbon_intensity": 250.0,
                "electricity_cost": 0.12,
                "gpu_availability": {"A100": 80, "V100": 150, "T4": 300},
                "cpu_availability": 1500,
                "memory_availability_gb": 7500.0,
                "renewable_sources": {"solar": 25.0, "wind": 15.0, "hydro": 15.0},
                "network_latency": {"us-west-1": 70, "eu-west-1": 80}
            },
            {
                "region_id": "eu-west-1",
                "name": "Europe West (Ireland)",
                "location": {"lat": 53.3498, "lng": -6.2603},
                "green_energy_score": 90.0,
                "renewable_percentage": 85.0,
                "carbon_intensity": 120.0,
                "electricity_cost": 0.18,
                "gpu_availability": {"A100": 30, "V100": 80, "T4": 150},
                "cpu_availability": 800,
                "memory_availability_gb": 4000.0,
                "renewable_sources": {"wind": 50.0, "solar": 15.0, "hydro": 20.0},
                "network_latency": {"us-east-1": 80, "us-west-1": 150}
            },
            {
                "region_id": "eu-north-1",
                "name": "Europe North (Sweden)",
                "location": {"lat": 59.3293, "lng": 18.0686},
                "green_energy_score": 95.0,
                "renewable_percentage": 90.0,
                "carbon_intensity": 80.0,
                "electricity_cost": 0.10,
                "gpu_availability": {"A100": 25, "V100": 60, "T4": 120},
                "cpu_availability": 600,
                "memory_availability_gb": 3000.0,
                "renewable_sources": {"hydro": 45.0, "wind": 35.0, "solar": 10.0},
                "network_latency": {"eu-west-1": 30, "us-east-1": 120}
            },
            {
                "region_id": "ap-southeast-1",
                "name": "Asia Pacific (Singapore)",
                "location": {"lat": 1.3521, "lng": 103.8198},
                "green_energy_score": 45.0,
                "renewable_percentage": 35.0,
                "carbon_intensity": 400.0,
                "electricity_cost": 0.20,
                "gpu_availability": {"A100": 40, "V100": 90, "T4": 180},
                "cpu_availability": 900,
                "memory_availability_gb": 4500.0,
                "renewable_sources": {"solar": 25.0, "wind": 5.0, "hydro": 5.0},
                "network_latency": {"us-west-1": 180, "eu-west-1": 200}
            }
        ]
        
        for region_data in sample_regions:
            region = Region(**region_data)
            db.add(region)
        
        db.commit()
        print("Database initialized with sample data")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

