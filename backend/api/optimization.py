from fastapi import APIRouter

from backend.service.optimization_service import get_optimization_suggestion
from backend.service.prompt_optimizer import optimize_prompt

router = APIRouter(prefix="/costops/optimize", tags=["Optimization"])

@router.post("/model")
def optimize_model(payload: dict):
    return get_optimization_suggestion(
        payload["model"],
        payload["input_tokens"],
        payload["output_tokens"]
    )


@router.post("/prompt")
def optimize_prompt_api(payload: dict):
    optimized = optimize_prompt(payload["prompt"])

    return {
        "original": payload["prompt"],
        "optimized": optimized
    }