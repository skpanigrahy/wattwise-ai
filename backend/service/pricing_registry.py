PRICING = {
    "gpt-4": {"input": 0.03 / 1000, "output": 0.06 / 1000},
    "gpt-4o-mini": {"input": 0.001 / 1000, "output": 0.002 / 1000},
    "claude-3": {"input": 0.008 / 1000, "output": 0.024 / 1000},
}

def get_pricing(model: str):
    return PRICING.get(model, {"input": 0.0, "output": 0.0})