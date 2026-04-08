from backend.service.llm_client import call_llm
from backend.service.cost_calculator import calculate_cost
from backend.service.quality_scorer import score_response

MODELS = ["gpt-4", "gpt-4o-mini", "claude-3"]

def benchmark_prompt(prompt: str):
    results = []

    for model in MODELS:
        response = call_llm(model, prompt)

        tokens = response["tokens_used"]

        cost = calculate_cost(model, tokens, tokens // 2)

        results.append({
            "model": model,
            "response": response["response"],
            "tokens": tokens,
            "cost": cost
        })

    return results



def benchmark_with_scoring(prompt: str):
    raw_results = benchmark_prompt(prompt)

    enriched = []

    for r in raw_results:
        quality = score_response(r["response"])

        enriched.append({
            **r,
            "quality_score": quality
        })

    return enriched