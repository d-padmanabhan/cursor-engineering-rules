# Security & Validation

## Security Scanning

**Security Scanning:** Use `bandit` to detect common security issues:

```bash
# Install
uv add --dev bandit
# or
pip install bandit

# Scan codebase
bandit -r .                    # Recursive scan
bandit -r . -f json -o report.json  # JSON output
bandit -r . -ll                # Low severity and above
bandit -r . -ii                # Medium confidence and above

# Exclude paths
bandit -r . -x tests/,venv/

# Use config file (.bandit)
bandit -r . -c .bandit
```

## Input Validation

**Input Validation:** Sanitize early with `re.match(r"^\w+$", user_input)`. For complex patterns, see [Making Regex Readable](#making-regex-readable) below.

**SQL Injection:** Use parameterized queries: `cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))`.

**Shell Sanitization:** Use `shlex.quote(user_input)` for shell commands.

```python
import shlex
import subprocess

# BAD: Shell injection vulnerability
subprocess.run(f"echo {user_input}", shell=True)

# GOOD: Use shlex.quote
subprocess.run(["echo", shlex.quote(user_input)])

# GOOD: Use list form (no shell)
subprocess.run(["echo", user_input])
```

## Pydantic Validation

**Pydantic:** Use for structured data validation:

```python
from pydantic import BaseModel, field_validator, HttpUrl

class User(BaseModel):
    name: str
    age: int
    email: str
    
    @field_validator("age")
    @classmethod
    def valid_age(cls, v: int) -> int:
        if v < 0 or v > 150:
            raise ValueError("Invalid age")
        return v
    
    @field_validator("email")
    @classmethod
    def valid_email(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("Invalid email format")
        return v.lower()

# Automatic validation
user = User(name="John", age=30, email="john@acme.com")
```

**Avoid Broad Exceptions:** Catch specific exceptions (`ValueError`, `KeyError`) instead of bare `except Exception`.

## Making Regex Readable

Regex patterns can become cryptic and hard to maintain. Use these techniques to make them self-documenting:

**Use Variables and Comments:**

```python
import re

# BAD: Cryptic regex
if re.match(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', email):
    ...

# GOOD: Self-documenting with variables
local_part = r'[a-zA-Z0-9._%+-]+'
domain_part = r'[a-zA-Z0-9.-]+'
tld = r'[a-zA-Z]{2,}'
email_pattern = rf'{local_part}@{domain_part}\.{tld}'

if re.match(email_pattern, email):
    ...

# EXCELLENT: Use VERBOSE flag for complex patterns
email_pattern = re.compile(r"""
    [a-zA-Z0-9._%+-]+      # Local part (username)
    @                       # @ symbol
    [a-zA-Z0-9.-]+         # Domain name
    \.                     # Literal dot
    [a-zA-Z]{2,}           # Top-level domain (2+ letters)
""", re.VERBOSE)

if email_pattern.match(email):
    ...
```

**Break Complex Patterns into Functions:**

```python
# BAD: One complex regex
if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
    ...

# GOOD: Validate components separately
def is_valid_email(email: str) -> bool:
    """Validate email format."""
    if not email or '@' not in email:
        return False

    local, domain = email.rsplit('@', 1)

    # Validate local part
    if not re.match(r'^[a-zA-Z0-9._%+-]+$', local):
        return False

    # Validate domain
    if not re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', domain):
        return False

    return True
```

**When Regex Gets Complex:**

For very complex validation patterns (>50 characters, multiple nested groups), consider:

1. **Break into smaller functions** - Validate components separately
2. **Use a validation library** - `pydantic`, `cerberus`, or `marshmallow` for structured validation
3. **Pregex** (optional) - For teams that frequently work with complex regex and need maximum readability

**Preference order:**

1. Simple stdlib `re` with variables/comments
2. `re.VERBOSE` flag for complex patterns
3. Validation library for structured data
4. Pregex only if regex is unavoidable and extremely complex

```python
# Example: Complex pattern broken down
# Pattern: Match URLs with optional protocol, domain, path, query, fragment

# Option 1: Use re.VERBOSE (preferred)
url_pattern = re.compile(r"""
    ^
    (?:https?://)?          # Optional protocol (http:// or https://)
    (?:www\.)?              # Optional www.
    [a-zA-Z0-9-]+          # Domain name
    (?:\.[a-zA-Z0-9-]+)*   # Optional subdomains
    \.[a-zA-Z]{2,}         # Top-level domain
    (?:/[^\s?#]*)?         # Optional path
    (?:\?[^\s#]*)?         # Optional query string
    (?:#[^\s]*)?           # Optional fragment
    $
""", re.VERBOSE)

# Option 2: Use validation library (better for structured data)
from pydantic import BaseModel, HttpUrl, field_validator

class Link(BaseModel):
    url: HttpUrl  # Automatic URL validation

    @field_validator('url', mode='before')
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v.startswith(('http://', 'https://')):
            return f'https://{v}'
        return v
```
