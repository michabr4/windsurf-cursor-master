def compile_intent_to_policy(intent: dict) -> dict:
    return {
        "policy_type": "connectivity",
        "match": {
            "source": intent["source"],
            "destination": intent["destination"]
        },
        "constraints": {
            "latency_sla_ms": intent.get("latency_sla_ms"),
            "bandwidth_mbps": intent.get("bandwidth_mbps")
        }
    }
