"""
Database management script for WattWise AI
"""

import os
import sys
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_tables():
    """Create all database tables"""
    from db.session import create_tables
    print("Creating database tables...")
    create_tables()
    print("Tables created successfully!")

def init_sample_data():
    """Initialize database with sample data"""
    from db.session import init_db
    print("Initializing database with sample data...")
    init_db()
    print("Sample data initialized successfully!")

def reset_database():
    """Reset the database (drop and recreate all tables)"""
    from sqlalchemy import create_engine, text
    from models.database import Base
    from db.session import DATABASE_URL
    
    print("Resetting database...")
    
    engine = create_engine(DATABASE_URL)
    
    # Drop all tables
    Base.metadata.drop_all(bind=engine)
    print("Dropped all tables")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Created all tables")
    
    # Initialize with sample data
    init_sample_data()
    print("Database reset complete!")

def check_connection():
    """Check database connection"""
    try:
        from db.session import SessionLocal
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        print("✅ Database connection successful!")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def show_stats():
    """Show database statistics"""
    try:
        from db.session import SessionLocal
        from models.database import Region, Workload
        
        db = SessionLocal()
        
        region_count = db.query(Region).count()
        workload_count = db.query(Workload).count()
        
        print(f"📊 Database Statistics:")
        print(f"   Regions: {region_count}")
        print(f"   Workloads: {workload_count}")
        
        # Show regions
        if region_count > 0:
            print(f"\n🌍 Regions:")
            regions = db.query(Region).all()
            for region in regions:
                print(f"   - {region.name} ({region.region_id}): {region.green_energy_score:.1f}% green")
        
        # Show recent workloads
        if workload_count > 0:
            print(f"\n🚀 Recent Workloads:")
            workloads = db.query(Workload).order_by(Workload.created_at.desc()).limit(5).all()
            for workload in workloads:
                print(f"   - {workload.name} ({workload.status}) in {workload.region_id or 'unassigned'}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error getting database stats: {e}")

def main():
    parser = argparse.ArgumentParser(description="WattWise AI Database Management")
    parser.add_argument(
        "command",
        choices=["create", "init", "reset", "check", "stats"],
        help="Database command to execute"
    )
    
    args = parser.parse_args()
    
    print(f"🗄️  WattWise AI Database Management")
    print(f"Database URL: {os.getenv('DATABASE_URL', 'Not set')}")
    print("-" * 50)
    
    if args.command == "create":
        create_tables()
    elif args.command == "init":
        init_sample_data()
    elif args.command == "reset":
        confirm = input("⚠️  This will delete all data. Are you sure? (y/N): ")
        if confirm.lower() == 'y':
            reset_database()
        else:
            print("Operation cancelled.")
    elif args.command == "check":
        check_connection()
    elif args.command == "stats":
        show_stats()

if __name__ == "__main__":
    main()

