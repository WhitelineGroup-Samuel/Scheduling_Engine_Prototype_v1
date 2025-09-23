# Testing Standards

## Test Philosophy
Our testing philosophy is to ensure correctness, stability, and performance through a comprehensive suite of automated tests. All tests should be deterministic, maintainable, and easy to interpret. We value fast feedback, high coverage, and clear intent in all our test code.

## Unit Tests
Unit tests are the foundation of our test suite. They should:
- Be written using `pytest`.
- Test individual functions or classes in strict isolation (no reliance on global state, real databases, or external services).
- Use mocks or fakes for dependencies.
- Use clear, descriptive function names.
- Be fast (<100ms each).

**Good Example:**
```python
def test_adds_two_numbers():
    assert add(2, 3) == 5
```

**Bad Example:**
```python
def test_add():
    # Relies on global state, unclear what is being tested
    assert global_addition(2) == 7
```

## Golden Tests
Golden (snapshot) tests verify that complex outputs (e.g., JSON, CSV) remain stable over time.
- Golden files must be checked into version control.
- Use deterministic seeds for any random data generation.
- If golden files change, the diff must be reviewed and justified in code review.
- Outputs must be canonicalized (sorted, formatted) to avoid spurious diffs.

**Good Example:**
```python
def test_generate_report_matches_golden(tmp_path):
    random.seed(42)
    output = generate_report(data, seed=42)
    golden_path = Path("tests/golden/reports/golden_report.json")
    assert json.loads(output) == json.loads(golden_path.read_text())
```

**Bad Example:**
```python
def test_report():
    # No seed, output can change on each run
    output = generate_report(data)
    with open("golden_report.json") as f:
        assert output == f.read()
```

## Property Tests
Property-based tests check that invariants hold across a wide range of inputs.
- Use tools like `hypothesis`.
- Clearly specify invariants (e.g., output is always sorted, never negative).
- Include property tests in CI.

Example:
```python
from hypothesis import given, strategies as st

@given(st.lists(st.integers()))
def test_sort_is_idempotent(xs):
    assert sorted(sorted(xs)) == sorted(xs)
```

## Performance Tests
Performance tests ensure key operations stay within defined time/memory budgets.
- Define explicit budgets (e.g., "must complete in <500ms for N=1000").
- Fail in CI if budgets are exceeded.
- Use deterministic seeds for reproducibility.

Example:
```python
import time

def test_large_sort_performance():
    random.seed(42)
    data = [random.random() for _ in range(100000)]
    start = time.time()
    sorted(data)
    assert time.time() - start < 0.5
```

## Coverage Targets
- Minimum overall test coverage: **90%**.
- Critical modules (core scheduling, payment logic, etc.): **≥95%**.
- Coverage is measured using `pytest-cov` or equivalent.
- Coverage is checked and enforced in CI.

## Workflow & Naming Conventions
- All tests live in `tests/` or alongside code as `test_*.py` files.
- Test function names must start with `test_` and clearly state intent.
- Use `pytest` fixtures for setup/teardown.
- Golden files should be placed under `tests/golden/`.
- All new features and bugfixes must include relevant tests.
