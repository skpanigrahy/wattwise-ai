"""
WattWise AI - Streamlit Frontend Dashboard
Main application entry point
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os

# Page configuration
st.set_page_config(
    page_title="WattWise AI",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #2E8B57;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f8f0;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2E8B57;
    }
    .status-scheduled {
        color: #FFA500;
    }
    .status-running {
        color: #32CD32;
    }
    .status-completed {
        color: #228B22;
    }
    .status-failed {
        color: #DC143C;
    }
</style>
""", unsafe_allow_html=True)

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Helper functions
@st.cache_data(ttl=60)
def fetch_region_scores():
    """Fetch region scores from backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/regions/scores")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch region scores: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error connecting to backend: {e}")
        return []

@st.cache_data(ttl=60)
def fetch_workloads():
    """Fetch workloads from backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/workloads")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch workloads: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error connecting to backend: {e}")
        return []

def query_assistant(query):
    """Query the AI assistant"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/agent/query",
            json={"query": query}
        )
        if response.status_code == 200:
            return response.json()["response"]
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Error: {e}"

def schedule_workload(workload_data):
    """Schedule a new workload"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/jobs/schedule",
            json=workload_data
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to schedule workload: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error scheduling workload: {e}")
        return None

# Sidebar navigation
st.sidebar.title("🌱 WattWise AI")
st.sidebar.markdown("Smart AI Workload Scheduler")

page = st.sidebar.selectbox(
    "Navigate to:",
    ["Dashboard", "Energy Forecast", "Region Map", "Schedule Workload", "AI Assistant"]
)

# Main content based on selected page
if page == "Dashboard":
    st.markdown('<h1 class="main-header">🌱 WattWise AI Dashboard</h1>', unsafe_allow_html=True)
    
    # Fetch data
    region_scores = fetch_region_scores()
    workloads = fetch_workloads()
    
    if region_scores:
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_green_score = sum(r["green_energy_score"] for r in region_scores) / len(region_scores)
            st.metric("Avg Green Energy Score", f"{avg_green_score:.1f}%")
        
        with col2:
            total_workloads = len(workloads)
            st.metric("Total Workloads", total_workloads)
        
        with col3:
            running_workloads = len([w for w in workloads if w["status"] == "running"])
            st.metric("Running Workloads", running_workloads)
        
        with col4:
            if workloads:
                total_emissions = sum(w.get("estimated_emissions", 0) for w in workloads)
                st.metric("Est. CO2 Emissions", f"{total_emissions:.2f} kg")
            else:
                st.metric("Est. CO2 Emissions", "0 kg")
        
        st.markdown("---")
        
        # Region scores chart
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🌍 Green Energy Scores by Region")
            df_regions = pd.DataFrame(region_scores)
            
            fig = px.bar(
                df_regions,
                x="region_name",
                y="green_energy_score",
                color="green_energy_score",
                color_continuous_scale="Greens",
                title="Green Energy Scores"
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("⚡ Carbon Intensity by Region")
            fig = px.bar(
                df_regions,
                x="region_name",
                y="carbon_intensity",
                color="carbon_intensity",
                color_continuous_scale="Reds_r",
                title="Carbon Intensity (gCO2/kWh)"
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        # Recent workloads
        st.subheader("📋 Recent Workloads")
        if workloads:
            df_workloads = pd.DataFrame(workloads)
            
            # Status color mapping
            status_colors = {
                "scheduled": "🟡",
                "running": "🟢",
                "completed": "✅",
                "failed": "❌",
                "pending": "⏳"
            }
            
            # Display workloads table
            for _, workload in df_workloads.head(10).iterrows():
                status_icon = status_colors.get(workload["status"], "⚪")
                col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                
                with col1:
                    st.write(f"{status_icon} **{workload['name']}**")
                    st.caption(f"Type: {workload['workload_type']}")
                
                with col2:
                    st.write(f"Region: {workload.get('region_id', 'N/A')}")
                
                with col3:
                    if workload.get('estimated_cost'):
                        st.write(f"Cost: ${workload['estimated_cost']:.2f}")
                    else:
                        st.write("Cost: N/A")
                
                with col4:
                    if workload.get('estimated_emissions'):
                        st.write(f"CO2: {workload['estimated_emissions']:.2f} kg")
                    else:
                        st.write("CO2: N/A")
                
                st.markdown("---")
        else:
            st.info("No workloads found. Schedule your first workload!")
    
    else:
        st.warning("Unable to connect to backend. Please check if the backend service is running.")

elif page == "Energy Forecast":
    st.markdown('<h1 class="main-header">📊 Energy Forecast</h1>', unsafe_allow_html=True)
    
    region_scores = fetch_region_scores()
    
    if region_scores:
        # Generate sample forecast data
        dates = pd.date_range(start=datetime.now(), periods=24, freq='H')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🌞 Renewable Energy Forecast")
            
            # Sample renewable energy forecast
            forecast_data = []
            for i, date in enumerate(dates):
                for region in region_scores[:3]:  # Top 3 regions
                    base_renewable = region["renewable_percentage"]
                    # Simulate daily variation
                    hour = date.hour
                    if 6 <= hour <= 18:  # Daytime
                        variation = 10 * (1 - abs(hour - 12) / 6)  # Peak at noon
                    else:
                        variation = -5
                    
                    forecast_data.append({
                        "datetime": date,
                        "region": region["region_name"],
                        "renewable_percentage": min(100, max(0, base_renewable + variation))
                    })
            
            df_forecast = pd.DataFrame(forecast_data)
            
            fig = px.line(
                df_forecast,
                x="datetime",
                y="renewable_percentage",
                color="region",
                title="24-Hour Renewable Energy Forecast"
            )
            fig.update_layout(yaxis_title="Renewable Energy %")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("💨 Carbon Intensity Forecast")
            
            # Sample carbon intensity forecast
            carbon_data = []
            for i, date in enumerate(dates):
                for region in region_scores[:3]:
                    base_carbon = region["carbon_intensity"]
                    # Simulate variation (lower during high renewable periods)
                    hour = date.hour
                    if 6 <= hour <= 18:
                        variation = -50 * (1 - abs(hour - 12) / 6)
                    else:
                        variation = 30
                    
                    carbon_data.append({
                        "datetime": date,
                        "region": region["region_name"],
                        "carbon_intensity": max(50, base_carbon + variation)
                    })
            
            df_carbon = pd.DataFrame(carbon_data)
            
            fig = px.line(
                df_carbon,
                x="datetime",
                y="carbon_intensity",
                color="region",
                title="24-Hour Carbon Intensity Forecast"
            )
            fig.update_layout(yaxis_title="Carbon Intensity (gCO2/kWh)")
            st.plotly_chart(fig, use_container_width=True)
        
        # Recommendations
        st.subheader("🎯 Optimal Scheduling Recommendations")
        
        # Find best times for each region
        best_times = df_forecast.groupby("region")["renewable_percentage"].idxmax()
        
        for region in region_scores[:3]:
            region_name = region["region_name"]
            best_idx = best_times[region_name]
            best_time = df_forecast.loc[best_idx, "datetime"]
            best_renewable = df_forecast.loc[best_idx, "renewable_percentage"]
            
            st.success(
                f"**{region_name}**: Best time to schedule workloads is "
                f"{best_time.strftime('%H:%M')} with {best_renewable:.1f}% renewable energy"
            )

elif page == "Region Map":
    st.markdown('<h1 class="main-header">🗺️ Global Region Map</h1>', unsafe_allow_html=True)
    
    region_scores = fetch_region_scores()
    
    if region_scores:
        # Create map data
        map_data = []
        for region in region_scores:
            # Sample coordinates (in real implementation, these would come from the database)
            coordinates = {
                "US West (California)": [37.7749, -122.4194],
                "US East (Virginia)": [38.9072, -77.0369],
                "Europe West (Ireland)": [53.3498, -6.2603],
                "Europe North (Sweden)": [59.3293, 18.0686],
                "Asia Pacific (Singapore)": [1.3521, 103.8198]
            }
            
            coord = coordinates.get(region["region_name"], [0, 0])
            map_data.append({
                "region": region["region_name"],
                "lat": coord[0],
                "lon": coord[1],
                "green_score": region["green_energy_score"],
                "renewable_pct": region["renewable_percentage"],
                "carbon_intensity": region["carbon_intensity"],
                "electricity_cost": region["electricity_cost"]
            })
        
        df_map = pd.DataFrame(map_data)
        
        # Create scatter plot on map
        fig = px.scatter_geo(
            df_map,
            lat="lat",
            lon="lon",
            size="green_score",
            color="green_score",
            hover_name="region",
            hover_data={
                "renewable_pct": ":.1f",
                "carbon_intensity": ":.0f",
                "electricity_cost": ":.3f"
            },
            color_continuous_scale="Greens",
            title="Global Green Energy Scores by Region"
        )
        
        fig.update_layout(
            geo=dict(
                showframe=False,
                showcoastlines=True,
                projection_type='equirectangular'
            ),
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Region details
        st.subheader("📊 Region Details")
        
        selected_region = st.selectbox(
            "Select a region for detailed information:",
            [r["region_name"] for r in region_scores]
        )
        
        if selected_region:
            region_data = next(r for r in region_scores if r["region_name"] == selected_region)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Green Energy Score", f"{region_data['green_energy_score']:.1f}%")
                st.metric("Renewable Energy", f"{region_data['renewable_percentage']:.1f}%")
            
            with col2:
                st.metric("Carbon Intensity", f"{region_data['carbon_intensity']:.0f} gCO2/kWh")
                st.metric("Electricity Cost", f"${region_data['electricity_cost']:.3f}/kWh")
            
            with col3:
                total_gpus = sum(region_data["gpu_availability"].values())
                st.metric("Total GPUs", total_gpus)
                st.metric("CPU Cores", region_data["cpu_availability"])
            
            # GPU availability breakdown
            st.subheader("🖥️ GPU Availability")
            gpu_df = pd.DataFrame([
                {"GPU Type": gpu_type, "Available": count}
                for gpu_type, count in region_data["gpu_availability"].items()
            ])
            
            if not gpu_df.empty:
                fig = px.bar(gpu_df, x="GPU Type", y="Available", title="Available GPUs by Type")
                st.plotly_chart(fig, use_container_width=True)

elif page == "Schedule Workload":
    st.markdown('<h1 class="main-header">🚀 Schedule New Workload</h1>', unsafe_allow_html=True)
    
    with st.form("schedule_workload"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Workload Name", placeholder="My AI Training Job")
            workload_type = st.selectbox(
                "Workload Type",
                ["llm_training", "llm_inference", "model_training", "batch_inference", "fine_tuning"]
            )
            priority = st.selectbox("Priority", ["low", "medium", "high", "critical"])
            duration = st.number_input("Estimated Duration (hours)", min_value=0.1, value=1.0, step=0.1)
        
        with col2:
            memory_gb = st.number_input("Memory (GB)", min_value=1, value=16, step=1)
            cpu_cores = st.number_input("CPU Cores", min_value=1, value=4, step=1)
            max_cost = st.number_input("Max Cost per Hour ($)", min_value=0.0, value=10.0, step=0.1)
            max_emissions = st.number_input("Max Carbon Emissions (kg CO2)", min_value=0.0, value=5.0, step=0.1)
        
        # GPU requirements
        st.subheader("GPU Requirements")
        gpu_col1, gpu_col2, gpu_col3 = st.columns(3)
        
        with gpu_col1:
            a100_count = st.number_input("A100 GPUs", min_value=0, value=0, step=1)
        with gpu_col2:
            v100_count = st.number_input("V100 GPUs", min_value=0, value=1, step=1)
        with gpu_col3:
            t4_count = st.number_input("T4 GPUs", min_value=0, value=0, step=1)
        
        # Preferred regions
        region_scores = fetch_region_scores()
        if region_scores:
            preferred_regions = st.multiselect(
                "Preferred Regions (optional)",
                [r["region_id"] for r in region_scores],
                format_func=lambda x: next(r["region_name"] for r in region_scores if r["region_id"] == x)
            )
        else:
            preferred_regions = []
        
        submitted = st.form_submit_button("Schedule Workload")
        
        if submitted:
            # Build GPU requirements
            gpu_requirements = {}
            if a100_count > 0:
                gpu_requirements["A100"] = a100_count
            if v100_count > 0:
                gpu_requirements["V100"] = v100_count
            if t4_count > 0:
                gpu_requirements["T4"] = t4_count
            
            workload_data = {
                "name": name,
                "workload_type": workload_type,
                "priority": priority,
                "estimated_duration_hours": duration,
                "gpu_requirements": gpu_requirements,
                "memory_gb": memory_gb,
                "cpu_cores": cpu_cores,
                "preferred_regions": preferred_regions if preferred_regions else None,
                "max_cost_per_hour": max_cost,
                "max_carbon_emissions": max_emissions
            }
            
            result = schedule_workload(workload_data)
            
            if result:
                st.success("✅ Workload scheduled successfully!")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"**Workload ID:** {result['workload_id']}")
                    st.info(f"**Recommended Region:** {result['recommended_region']}")
                    st.info(f"**Estimated Cost:** ${result['estimated_cost']:.2f}")
                
                with col2:
                    st.info(f"**Estimated Start:** {result['estimated_start_time']}")
                    st.info(f"**Green Energy Score:** {result['green_energy_score']:.1f}%")
                    st.info(f"**Estimated Emissions:** {result['estimated_emissions']:.2f} kg CO2")
                
                st.markdown("**Reasoning:**")
                st.write(result['reasoning'])

elif page == "AI Assistant":
    st.markdown('<h1 class="main-header">🤖 AI Assistant</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    Ask me anything about green computing, energy optimization, or workload scheduling!
    
    **Example queries:**
    - "Which region has the best green energy score?"
    - "Show me GPU availability across regions"
    - "How can I optimize costs for my AI workload?"
    - "What's the carbon impact of running in different regions?"
    """)
    
    # Chat interface
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me about green computing..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = query_assistant(prompt)
            st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**WattWise AI v1.0**")
st.sidebar.markdown("Smart AI Workload Scheduler")
st.sidebar.markdown("🌱 Optimizing for green energy")

if __name__ == "__main__":
    pass

