# Testing Patterns

## pytest Basics

```python
def test_parse_input():
    assert parse_input("123") == 123

def test_parse_invalid_raises():
    with pytest.raises(ValueError):
        parse_input("invalid")
```

## Parameterized Tests

```python
import pytest

@pytest.mark.parametrize("input,expected", [
    ("123", 123),
    ("456", 456),
    ("-1", -1),
])
def test_parse_multiple_inputs(input: str, expected: int):
    assert parse_input(input) == expected
```

## Fixtures

```python
import pytest

@pytest.fixture
def sample_user():
    return User(name="Alice", age=30)

@pytest.fixture
def db_connection():
    conn = create_connection()
    yield conn
    conn.close()

def test_user_creation(sample_user):
    assert sample_user.name == "Alice"

def test_database_query(db_connection):
    result = db_connection.execute("SELECT 1")
    assert result is not None
```

## Mocking

```python
from unittest.mock import patch, MagicMock

def test_api_call():
    with patch("module.requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"status": "ok"}
        result = fetch_status()
        assert result == "ok"
        mock_get.assert_called_once()

def test_boto3_client():
    mock_s3 = MagicMock()
    mock_s3.list_buckets.return_value = {"Buckets": []}
    
    with patch("module.boto3.client", return_value=mock_s3):
        result = list_all_buckets()
        assert result == []
```

## Testing Async Code

```python
import pytest

@pytest.mark.asyncio
async def test_async_fetch():
    result = await fetch_data("https://api.acme.com/data")
    assert result["status"] == "ok"
```

## Test Organization

```
tests/
├── conftest.py          # Shared fixtures
├── test_models.py       # Unit tests for models
├── test_services.py     # Unit tests for services
├── test_api.py          # API integration tests
└── test_integration/    # Integration tests
    └── test_e2e.py
```

## conftest.py Example

```python
import pytest

@pytest.fixture(scope="session")
def app_config():
    return {"debug": True, "db": "test.db"}

@pytest.fixture(scope="function")
def clean_database(app_config):
    db = connect(app_config["db"])
    yield db
    db.clear_all()
    db.close()
```

## Coverage

```bash
# Run tests with coverage
pytest --cov=mymodule --cov-report=html

# Require minimum coverage
pytest --cov=mymodule --cov-fail-under=80
```

## Testing Best Practices

1. **Arrange-Act-Assert (AAA)** pattern
2. **One assertion per test** (when practical)
3. **Descriptive test names**: `test_user_creation_with_invalid_email_raises_error`
4. **Isolate tests**: No shared state between tests
5. **Fast tests**: Mock external dependencies
6. **Test edge cases**: Empty inputs, None values, boundary conditions

## Mocking AWS Services

```python
from unittest.mock import patch, MagicMock
import pytest

@pytest.fixture
def mock_s3():
    with patch("boto3.client") as mock_client:
        mock_s3 = MagicMock()
        mock_client.return_value = mock_s3
        yield mock_s3

def test_upload_file(mock_s3):
    mock_s3.upload_file.return_value = None
    
    result = upload_to_s3("local.txt", "bucket", "key")
    
    assert result is True
    mock_s3.upload_file.assert_called_once_with(
        "local.txt", "bucket", "key"
    )
```

## Property-Based Testing

```python
from hypothesis import given, strategies as st

@given(st.integers())
def test_absolute_value_is_non_negative(x: int):
    assert abs(x) >= 0

@given(st.lists(st.integers()))
def test_sorted_list_is_sorted(xs: list[int]):
    result = sorted(xs)
    assert all(result[i] <= result[i+1] for i in range(len(result)-1))
```
