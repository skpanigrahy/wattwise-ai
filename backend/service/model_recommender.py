MODEL_MAPPING = {
    "gpt-4": "gpt-4o-mini",
    "claude-3": "gpt-4o-mini"
}

def recommend_model(current_model: str):
    return MODEL_MAPPING.get(current_model, current_model)