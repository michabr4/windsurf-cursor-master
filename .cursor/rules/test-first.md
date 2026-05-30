# Test-First Development Protocol

## Requirement

For any new function, class, or agent component: write the test BEFORE the implementation.

## Process

1. Read the "Test Criteria" section from the Comms Bridge task spec
2. Write failing tests covering each criterion
3. Implement the code to make tests pass
4. Report in result: "Tests written first: [list], all passing: [YES/NO]"

## Test File Conventions

- Location: `tests/test_[module].py`
- Naming: `test_[what_it_does]_[when_condition]()`
- Example: `test_delivery_tracker_returns_empty_when_no_milestones()`

## Minimum Coverage Per Agent

- Happy path: 1+ tests
- Error path (API down, bad input): 1+ tests
- Auth failure: 1 test
- Edge case (empty data, null fields): 1+ tests

## Example Test Structure

```python
import pytest
from agents.delivery_tracker.agent import DeliveryTracker

def test_delivery_tracker_returns_milestones_on_success():
    tracker = DeliveryTracker(project_id="test-001")
    result = tracker.run()
    assert isinstance(result, list)
    assert len(result) > 0

def test_delivery_tracker_handles_empty_project():
    tracker = DeliveryTracker(project_id="empty-project")
    result = tracker.run()
    assert result == []

def test_delivery_tracker_raises_on_auth_failure(monkeypatch):
    monkeypatch.setenv("HELIX_API_TOKEN", "invalid-token")
    tracker = DeliveryTracker(project_id="test-001")
    with pytest.raises(Exception):
        tracker.run()
```

## Skipping Tests

Only skip with explicit permission from Windsurf in the task spec.
Always note in result: `"Tests skipped: [reason]"`
