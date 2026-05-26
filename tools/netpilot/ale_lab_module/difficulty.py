def adjust_difficulty(performance: dict) -> str:
    score = performance.get("score", 0)
    if score > 80:
        return "advanced"
    if score > 50:
        return "intermediate"
    return "beginner"
