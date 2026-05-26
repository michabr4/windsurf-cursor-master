def risk_score(predictions, thresholds) -> float:
    # simple example: max predicted utilization vs threshold
    max_val = max(p["value"] for p in predictions)
    return min(1.0, max_val / thresholds.get("max_utilization", 100))
