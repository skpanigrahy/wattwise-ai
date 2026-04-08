def score_response(response: str):
    """
    Simple heuristic scoring:
    - length
    - keyword presence
    """

    score = 0

    if len(response) > 50:
        score += 5

    if "example" in response.lower():
        score += 3

    if "explain" in response.lower():
        score += 2

    return min(score, 10)