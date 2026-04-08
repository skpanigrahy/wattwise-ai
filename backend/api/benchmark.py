from fastapi import APIRouter
from backend.service.benchmarking_service import benchmark_with_scoring
from backend.service.prompt_rewriter import rewrite_prompt

router = APIRouter(prefix="/costops/advanced", tags=["Advanced"])

@router.post("/benchmark")
def benchmark(payload: dict):
    return benchmark_with_scoring(payload["prompt"])


@router.post("/rewrite")
def rewrite(payload: dict):
    return {
        "optimized_prompt": rewrite_prompt(payload["prompt"])
    }