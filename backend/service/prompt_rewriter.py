#LLM Client (Unified Entry Point)
#This abstracts OpenAI / Claude / etc.
#Later plug:
# Azure OpenAI
# OpenAI API
# Anthropic

import os
from backend.service.llm_client import call_llm

def rewrite_prompt(prompt: str):
    """
    Uses LLM to rewrite prompt efficiently
    """

    instruction = f"""
    Rewrite this prompt to be shorter and more cost-efficient
    while preserving meaning:

    {prompt}
    """

    result = call_llm("gpt-4o-mini", instruction)

    return result["response"]

def call_llm(model: str, prompt: str):
    """
    Mock implementation (replace with real API later)
    """

    # Simulated response
    return {
        "model": model,
        "response": f"Response from {model} for: {prompt}",
        "tokens_used": len(prompt.split()) * 2
    }