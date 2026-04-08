"""
Green Compute Assistant - LangChain-powered AI assistant for green computing queries
"""

import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema import BaseMessage
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

class GreenEnergyTool(BaseTool):
    """Tool for querying green energy scores and regional data"""
    
    name = "green_energy_query"
    description = "Get green energy scores, renewable percentages, and carbon intensity for regions"
    
    def _run(self, query: str) -> str:
        """Execute the tool"""
        # This would typically query the database
        # For now, return sample data
        sample_data = {
            "us-west-1": {
                "green_energy_score": 85.0,
                "renewable_percentage": 75.0,
                "carbon_intensity": 150.0,
                "renewable_sources": {"solar": 45.0, "wind": 20.0, "hydro": 10.0}
            },
            "eu-north-1": {
                "green_energy_score": 95.0,
                "renewable_percentage": 90.0,
                "carbon_intensity": 80.0,
                "renewable_sources": {"hydro": 45.0, "wind": 35.0, "solar": 10.0}
            },
            "ap-southeast-1": {
                "green_energy_score": 45.0,
                "renewable_percentage": 35.0,
                "carbon_intensity": 400.0,
                "renewable_sources": {"solar": 25.0, "wind": 5.0, "hydro": 5.0}
            }
        }
        
        if "best" in query.lower() or "highest" in query.lower():
            best_region = max(sample_data.items(), key=lambda x: x[1]["green_energy_score"])
            return f"The region with the highest green energy score is {best_region[0]} with {best_region[1]['green_energy_score']}% green energy score and {best_region[1]['renewable_percentage']}% renewable energy."
        
        if "worst" in query.lower() or "lowest" in query.lower():
            worst_region = min(sample_data.items(), key=lambda x: x[1]["green_energy_score"])
            return f"The region with the lowest green energy score is {worst_region[0]} with {worst_region[1]['green_energy_score']}% green energy score and {worst_region[1]['renewable_percentage']}% renewable energy."
        
        # Return overview of all regions
        result = "Current green energy status by region:\n"
        for region, data in sample_data.items():
            result += f"- {region}: {data['green_energy_score']}% green energy score, {data['renewable_percentage']}% renewable, {data['carbon_intensity']} gCO2/kWh\n"
        
        return result

class GPUAvailabilityTool(BaseTool):
    """Tool for querying GPU availability across regions"""
    
    name = "gpu_availability_query"
    description = "Get GPU availability and compute resource status for regions"
    
    def _run(self, query: str) -> str:
        """Execute the tool"""
        sample_gpu_data = {
            "us-west-1": {"A100": 50, "V100": 100, "T4": 200, "cpu_cores": 1000},
            "us-east-1": {"A100": 80, "V100": 150, "T4": 300, "cpu_cores": 1500},
            "eu-west-1": {"A100": 30, "V100": 80, "T4": 150, "cpu_cores": 800},
            "eu-north-1": {"A100": 25, "V100": 60, "T4": 120, "cpu_cores": 600},
            "ap-southeast-1": {"A100": 40, "V100": 90, "T4": 180, "cpu_cores": 900}
        }
        
        if "a100" in query.lower():
            result = "A100 GPU availability:\n"
            for region, gpus in sample_gpu_data.items():
                result += f"- {region}: {gpus['A100']} A100 GPUs available\n"
            return result
        
        if "total" in query.lower() or "summary" in query.lower():
            result = "GPU availability summary:\n"
            for region, gpus in sample_gpu_data.items():
                total_gpus = gpus["A100"] + gpus["V100"] + gpus["T4"]
                result += f"- {region}: {total_gpus} total GPUs ({gpus['A100']} A100, {gpus['V100']} V100, {gpus['T4']} T4), {gpus['cpu_cores']} CPU cores\n"
            return result
        
        # Default: return all GPU data
        result = "Current GPU availability by region:\n"
        for region, gpus in sample_gpu_data.items():
            result += f"- {region}: A100: {gpus['A100']}, V100: {gpus['V100']}, T4: {gpus['T4']}, CPU cores: {gpus['cpu_cores']}\n"
        
        return result

class CostOptimizationTool(BaseTool):
    """Tool for cost optimization recommendations"""
    
    name = "cost_optimization"
    description = "Provide cost optimization recommendations for AI workloads"
    
    def _run(self, query: str) -> str:
        """Execute the tool"""
        cost_data = {
            "us-west-1": {"electricity_cost": 0.15, "green_premium": 0.02},
            "us-east-1": {"electricity_cost": 0.12, "green_premium": 0.01},
            "eu-west-1": {"electricity_cost": 0.18, "green_premium": 0.03},
            "eu-north-1": {"electricity_cost": 0.10, "green_premium": 0.01},
            "ap-southeast-1": {"electricity_cost": 0.20, "green_premium": 0.05}
        }
        
        if "cheapest" in query.lower() or "lowest cost" in query.lower():
            cheapest = min(cost_data.items(), key=lambda x: x[1]["electricity_cost"])
            return f"The most cost-effective region is {cheapest[0]} with electricity cost of ${cheapest[1]['electricity_cost']:.3f}/kWh."
        
        if "expensive" in query.lower() or "highest cost" in query.lower():
            expensive = max(cost_data.items(), key=lambda x: x[1]["electricity_cost"])
            return f"The most expensive region is {expensive[0]} with electricity cost of ${expensive[1]['electricity_cost']:.3f}/kWh."
        
        # Cost optimization recommendations
        recommendations = [
            "Cost optimization strategies:",
            "1. Schedule workloads during off-peak hours (typically 10 PM - 6 AM)",
            "2. Use spot instances for non-critical batch jobs",
            "3. Consider regions with high renewable energy for long-term cost stability",
            "4. Implement auto-scaling to optimize resource utilization",
            "5. Use mixed instance types based on workload requirements"
        ]
        
        result = "\n".join(recommendations) + "\n\nCurrent electricity costs by region:\n"
        for region, data in cost_data.items():
            result += f"- {region}: ${data['electricity_cost']:.3f}/kWh\n"
        
        return result

class GreenComputeAssistant:
    """
    LangChain-powered assistant for green computing queries
    """
    
    def __init__(self):
        # Initialize OpenAI LLM (fallback to a simple response if no API key)
        self.llm = None
        self.agent_executor = None
        
        # Try to initialize with OpenAI
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key:
            try:
                self.llm = ChatOpenAI(
                    temperature=0.1,
                    model_name="gpt-3.5-turbo",
                    openai_api_key=openai_api_key
                )
                self._setup_agent()
            except Exception as e:
                print(f"Warning: Could not initialize OpenAI LLM: {e}")
        
        # Initialize tools
        self.tools = [
            GreenEnergyTool(),
            GPUAvailabilityTool(),
            CostOptimizationTool()
        ]
    
    def _setup_agent(self):
        """Setup the LangChain agent with tools"""
        if not self.llm:
            return
        
        # Create the prompt template
        template = """You are WattWise AI Assistant, an expert in green computing and sustainable AI workload optimization.

You help users make informed decisions about where and when to run AI workloads to minimize environmental impact while optimizing for cost and performance.

You have access to the following tools:
{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought: {agent_scratchpad}"""

        prompt = PromptTemplate.from_template(template)
        
        try:
            # Create the agent
            agent = create_react_agent(self.llm, self.tools, prompt)
            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=self.tools,
                verbose=True,
                max_iterations=3,
                handle_parsing_errors=True
            )
        except Exception as e:
            print(f"Warning: Could not setup agent: {e}")
    
    async def query(self, query: str) -> str:
        """
        Process a query and return a response
        """
        try:
            if self.agent_executor:
                # Use the LangChain agent
                result = self.agent_executor.invoke({"input": query})
                return result.get("output", "I apologize, but I couldn't process your query.")
            else:
                # Fallback to simple rule-based responses
                return self._fallback_response(query)
        
        except Exception as e:
            print(f"Error processing query: {e}")
            return self._fallback_response(query)
    
    def _fallback_response(self, query: str) -> str:
        """
        Fallback response when LangChain agent is not available
        """
        query_lower = query.lower()
        
        # Green energy queries
        if any(word in query_lower for word in ["green", "renewable", "clean", "sustainable"]):
            tool = GreenEnergyTool()
            return tool._run(query)
        
        # GPU/resource queries
        elif any(word in query_lower for word in ["gpu", "compute", "resource", "availability"]):
            tool = GPUAvailabilityTool()
            return tool._run(query)
        
        # Cost queries
        elif any(word in query_lower for word in ["cost", "price", "cheap", "expensive", "optimize"]):
            tool = CostOptimizationTool()
            return tool._run(query)
        
        # General recommendations
        elif any(word in query_lower for word in ["recommend", "suggest", "best", "where", "when"]):
            return self._general_recommendations()
        
        # Default response
        else:
            return """I'm WattWise AI Assistant, here to help you optimize AI workloads for green energy efficiency!

I can help you with:
- 🌱 Green energy scores and renewable energy data by region
- 💻 GPU availability and compute resource status
- 💰 Cost optimization strategies
- 📊 Carbon emissions analysis
- 🎯 Workload placement recommendations

Try asking me:
- "Which region has the best green energy score?"
- "Show me GPU availability across regions"
- "How can I optimize costs for my AI workload?"
- "What's the carbon impact of running in different regions?"

What would you like to know about green computing?"""
    
    def _general_recommendations(self) -> str:
        """
        Provide general green computing recommendations
        """
        return """🌱 Green Computing Recommendations:

**For Maximum Environmental Impact:**
- Choose regions with high renewable energy (EU North, US West)
- Schedule workloads during peak renewable generation (sunny/windy periods)
- Use efficient GPU types (A100 for training, T4 for inference)

**For Cost Optimization:**
- Consider EU North (Sweden) for low electricity costs
- Use spot instances for batch workloads
- Schedule during off-peak hours

**For Balanced Approach:**
- EU West (Ireland) offers good green energy with reasonable costs
- US West (California) provides high renewable energy with good GPU availability

**Best Practices:**
1. Monitor real-time green energy scores
2. Use auto-scaling to minimize idle resources
3. Implement workload queuing for optimal timing
4. Consider carbon offset programs for unavoidable emissions

Would you like specific recommendations for your workload type?"""

