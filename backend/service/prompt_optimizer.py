def optimize_prompt(prompt: str) -> str:
    """
    Simple optimization:
    - remove filler words
    - shorten instructions
    """

    replacements = {
        "please explain in detail": "explain briefly",
        "can you provide a detailed explanation": "explain briefly",
        "in a very detailed manner": "briefly"
    }

    optimized = prompt.lower()

    for k, v in replacements.items():
        optimized = optimized.replace(k, v)

    return optimized