from backend.service.pricing_registry import get_pricing

def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    pricing = get_pricing(model)

    input_cost = input_tokens * pricing["input"]
    output_cost = output_tokens * pricing["output"]

    return round(input_cost + output_cost, 6)