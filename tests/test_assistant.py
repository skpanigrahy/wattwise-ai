"""
Tests for WattWise AI Assistant
"""

import pytest
from agent.assistant import GreenComputeAssistant, GreenEnergyTool, GPUAvailabilityTool, CostOptimizationTool

@pytest.fixture
def assistant():
    """Create GreenComputeAssistant instance"""
    return GreenComputeAssistant()

@pytest.fixture
def green_energy_tool():
    """Create GreenEnergyTool instance"""
    return GreenEnergyTool()

@pytest.fixture
def gpu_tool():
    """Create GPUAvailabilityTool instance"""
    return GPUAvailabilityTool()

@pytest.fixture
def cost_tool():
    """Create CostOptimizationTool instance"""
    return CostOptimizationTool()

def test_green_energy_tool_best_region(green_energy_tool):
    """Test green energy tool for best region query"""
    result = green_energy_tool._run("Which region has the best green energy score?")
    
    assert isinstance(result, str)
    assert len(result) > 0
    assert "highest" in result.lower() or "best" in result.lower()
    assert "eu-north-1" in result  # Should identify the best region

def test_green_energy_tool_worst_region(green_energy_tool):
    """Test green energy tool for worst region query"""
    result = green_energy_tool._run("Which region has the worst green energy score?")
    
    assert isinstance(result, str)
    assert len(result) > 0
    assert "lowest" in result.lower() or "worst" in result.lower()
    assert "ap-southeast-1" in result  # Should identify the worst region

def test_green_energy_tool_overview(green_energy_tool):
    """Test green energy tool for overview query"""
    result = green_energy_tool._run("Show me all regions")
    
    assert isinstance(result, str)
    assert len(result) > 0
    assert "us-west-1" in result
    assert "eu-north-1" in result
    assert "ap-southeast-1" in result
    assert "green energy score" in result.lower()

def test_gpu_availability_tool_a100(gpu_tool):
    """Test GPU availability tool for A100 query"""
    result = gpu_tool._run("How many A100 GPUs are available?")
    
    assert isinstance(result, str)
    assert len(result) > 0
    assert "A100" in result
    assert "available" in result.lower()

def test_gpu_availability_tool_summary(gpu_tool):
    """Test GPU availability tool for summary query"""
    result = gpu_tool._run("Show me total GPU availability")
    
    assert isinstance(result, str)
    assert len(result) > 0
    assert "total" in result.lower()
    assert "A100" in result
    assert "V100" in result
    assert "T4" in result

def test_gpu_availability_tool_default(gpu_tool):
    """Test GPU availability tool default response"""
    result = gpu_tool._run("GPU status")
    
    assert isinstance(result, str)
    assert len(result) > 0
    assert "A100" in result
    assert "V100" in result
    assert "T4" in result

def test_cost_optimization_tool_cheapest(cost_tool):
    """Test cost optimization tool for cheapest region"""
    result = cost_tool._run("Which region is the cheapest?")
    
    assert isinstance(result, str)
    assert len(result) > 0
    assert "cost-effective" in result.lower() or "cheapest" in result.lower()
    assert "eu-north-1" in result  # Should identify the cheapest region

def test_cost_optimization_tool_expensive(cost_tool):
    """Test cost optimization tool for most expensive region"""
    result = cost_tool._run("Which region is the most expensive?")
    
    assert isinstance(result, str)
    assert len(result) > 0
    assert "expensive" in result.lower()
    assert "ap-southeast-1" in result  # Should identify the most expensive region

def test_cost_optimization_tool_recommendations(cost_tool):
    """Test cost optimization tool for general recommendations"""
    result = cost_tool._run("How can I optimize costs?")
    
    assert isinstance(result, str)
    assert len(result) > 0
    assert "optimization" in result.lower()
    assert "strategies" in result.lower() or "recommendations" in result.lower()

@pytest.mark.asyncio
async def test_assistant_green_energy_query(assistant):
    """Test assistant with green energy query"""
    response = await assistant.query("Which region has the best green energy score?")
    
    assert isinstance(response, str)
    assert len(response) > 0
    # Should contain information about green energy

@pytest.mark.asyncio
async def test_assistant_gpu_query(assistant):
    """Test assistant with GPU query"""
    response = await assistant.query("Show me GPU availability")
    
    assert isinstance(response, str)
    assert len(response) > 0
    # Should contain GPU information

@pytest.mark.asyncio
async def test_assistant_cost_query(assistant):
    """Test assistant with cost query"""
    response = await assistant.query("How can I optimize costs?")
    
    assert isinstance(response, str)
    assert len(response) > 0
    # Should contain cost optimization information

@pytest.mark.asyncio
async def test_assistant_recommendation_query(assistant):
    """Test assistant with recommendation query"""
    response = await assistant.query("Recommend the best region for my workload")
    
    assert isinstance(response, str)
    assert len(response) > 0
    # Should contain recommendations

@pytest.mark.asyncio
async def test_assistant_general_query(assistant):
    """Test assistant with general query"""
    response = await assistant.query("What is WattWise AI?")
    
    assert isinstance(response, str)
    assert len(response) > 0
    assert "WattWise" in response or "green" in response.lower()

@pytest.mark.asyncio
async def test_assistant_fallback_response(assistant):
    """Test assistant fallback response"""
    response = await assistant.query("Random unrelated query")
    
    assert isinstance(response, str)
    assert len(response) > 0
    # Should provide helpful fallback response

def test_assistant_tools_initialization(assistant):
    """Test that assistant tools are properly initialized"""
    assert len(assistant.tools) == 3
    
    tool_names = [tool.name for tool in assistant.tools]
    assert "green_energy_query" in tool_names
    assert "gpu_availability_query" in tool_names
    assert "cost_optimization" in tool_names

def test_green_energy_tool_properties(green_energy_tool):
    """Test green energy tool properties"""
    assert green_energy_tool.name == "green_energy_query"
    assert "green energy" in green_energy_tool.description.lower()

def test_gpu_tool_properties(gpu_tool):
    """Test GPU tool properties"""
    assert gpu_tool.name == "gpu_availability_query"
    assert "gpu" in gpu_tool.description.lower()

def test_cost_tool_properties(cost_tool):
    """Test cost tool properties"""
    assert cost_tool.name == "cost_optimization"
    assert "cost" in cost_tool.description.lower()

