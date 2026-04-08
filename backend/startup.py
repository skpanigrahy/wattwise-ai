"""
Startup script for WattWise AI backend
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def initialize_database():
    """Initialize the database with sample data"""
    try:
        from db.session import init_db
        print("Initializing database...")
        init_db()
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False
    return True

def start_server():
    """Start the FastAPI server"""
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "true").lower() == "true"
    
    print(f"Starting WattWise AI server on port {port}...")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=debug,
        log_level="info"
    )

if __name__ == "__main__":
    # Initialize database first
    if initialize_database():
        # Start the server
        start_server()
    else:
        print("Failed to initialize database. Exiting.")
        sys.exit(1)

