def validate_intent(intent: dict, schema: dict) -> bool:
    required = [f["name"] for f in schema["fields"] if f.get("required")]
    for field in required:
        if field not in intent:
            return False
    # add type checks, constraint checks, etc.
    return True
