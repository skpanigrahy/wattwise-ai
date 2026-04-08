from backend.service.model_recommender import recommend_model
from backend.service.cost_calculator import calculate_cost

def estimate_cost(model, input_tokens, output_tokens):
    return calculate_cost(model, input_tokens, output_tokens)


def get_optimization_suggestion(model, input_tokens, output_tokens):
    current_cost = estimate_cost(model, input_tokens, output_tokens)

    recommended_model = recommend_model(model)

    if recommended_model == model:
        return {
            "message": "Current model is already optimal",
            "savings": 0
        }

    new_cost = estimate_cost(recommended_model, input_tokens, output_tokens)

    savings = current_cost - new_cost

    return {
        "current_model": model,
        "recommended_model": recommended_model,
        "current_cost": current_cost,
        "estimated_cost": new_cost,
        "savings": round(savings, 6)
    }