"""
Startup script for WattWise AI frontend
"""

import os
import subprocess
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def start_streamlit():
    """Start the Streamlit application"""
    port = int(os.getenv("PORT", 8501))
    
    print(f"Starting WattWise AI frontend on port {port}...")
    
    # Set environment variables for Streamlit
    env = os.environ.copy()
    env["STREAMLIT_SERVER_PORT"] = str(port)
    env["STREAMLIT_SERVER_ADDRESS"] = "0.0.0.0"
    env["STREAMLIT_SERVER_HEADLESS"] = "true"
    env["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    
    # Start Streamlit
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.port", str(port),
        "--server.address", "0.0.0.0",
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false"
    ], env=env)

if __name__ == "__main__":
    start_streamlit()

