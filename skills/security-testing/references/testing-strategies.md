# Testing Strategies

## Unit Testing

```python
import pytest

# Simple test
def test_add():
    assert add(2, 3) == 5

# Test with fixtures
@pytest.fixture
def user():
    return User(name="Alice", email="alice@acme.com")

def test_user_greeting(user):
    assert user.greeting() == "Hello, Alice!"

# Parameterized tests
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("World", "WORLD"),
    ("", ""),
])
def test_uppercase(input, expected):
    assert uppercase(input) == expected

# Testing exceptions
def test_division_by_zero():
    with pytest.raises(ZeroDivisionError):
        divide(1, 0)
```

## Mocking

```python
from unittest.mock import Mock, patch, MagicMock

# Mock external service
@patch("module.requests.get")
def test_fetch_user(mock_get):
    mock_get.return_value.json.return_value = {"name": "Alice"}
    mock_get.return_value.status_code = 200
    
    user = fetch_user(123)
    
    assert user["name"] == "Alice"
    mock_get.assert_called_once_with("https://api.acme.com/users/123")

# Mock database
@patch("module.db")
def test_create_user(mock_db):
    mock_db.insert.return_value = {"id": 1}
    
    result = create_user({"name": "Bob"})
    
    assert result["id"] == 1
```

## Integration Testing

```python
import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def client():
    from app import app
    return TestClient(app)

@pytest.fixture
def db():
    # Setup test database
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield Session(engine)
    # Teardown

def test_create_and_get_user(client, db):
    # Create
    response = client.post("/users", json={"name": "Alice"})
    assert response.status_code == 201
    user_id = response.json()["id"]
    
    # Get
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Alice"
```

## E2E Testing

```python
from playwright.sync_api import sync_playwright

def test_login_flow():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # Navigate to login
        page.goto("https://app.acme.com/login")
        
        # Fill form
        page.fill("[name=email]", "user@acme.com")
        page.fill("[name=password]", "password123")
        page.click("button[type=submit]")
        
        # Verify redirect
        page.wait_for_url("**/dashboard")
        assert page.locator("h1").text_content() == "Dashboard"
        
        browser.close()
```

## Test Coverage

```bash
# Run with coverage
pytest --cov=src --cov-report=html

# Minimum coverage requirement
pytest --cov=src --cov-fail-under=80
```

## Test Organization

```
tests/
├── conftest.py           # Shared fixtures
├── unit/
│   ├── test_models.py
│   └── test_services.py
├── integration/
│   ├── test_api.py
│   └── test_database.py
└── e2e/
    └── test_flows.py
```

## Test Naming

```python
# Pattern: test_<what>_<condition>_<expected>
def test_create_user_with_valid_data_returns_user():
    pass

def test_create_user_with_empty_name_raises_error():
    pass

def test_login_with_invalid_password_returns_401():
    pass
```

## Property-Based Testing

```python
from hypothesis import given, strategies as st

@given(st.integers(), st.integers())
def test_addition_commutative(a, b):
    assert add(a, b) == add(b, a)

@given(st.lists(st.integers()))
def test_sorted_output_has_same_length(items):
    result = sort(items)
    assert len(result) == len(items)
```
