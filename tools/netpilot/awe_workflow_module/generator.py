def generate_workflow(intent: dict, pattern_id: str) -> dict:
    # select pattern, inject vendor/context, return workflow spec
    return {
        "name": f"auto_workflow_{pattern_id}",
        "steps": [
            {"id": "validate_intent", "engine": "IBNL"},
            {"id": "generate_config", "engine": "ANE"},
            {"id": "push_config", "engine": "AREX"},
            {"id": "verify_telemetry", "engine": "PTE"},
            {"id": "remediate_if_needed", "engine": "AREX"}
        ]
    }
