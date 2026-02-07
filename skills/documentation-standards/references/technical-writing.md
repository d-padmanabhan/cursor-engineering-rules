# Technical Writing

## Document Types

### README

- Project overview and purpose
- Installation instructions
- Quick start guide
- Links to detailed docs

### API Documentation

- Endpoint descriptions
- Request/response examples
- Error codes
- Authentication

### Architecture Decision Records (ADRs)

- Context and problem
- Decision made
- Consequences
- Status

### Runbooks

- Step-by-step procedures
- Troubleshooting guides
- Emergency responses

## ADR Template

```markdown
# ADR-001: Use PostgreSQL for Primary Database

## Status

Accepted

## Context

We need a database for our application. Requirements:
- ACID compliance
- JSON support
- Strong ecosystem

## Decision

We will use PostgreSQL as our primary database.

## Consequences

### Positive
- Mature, well-documented
- Strong JSON support with JSONB
- Excellent performance for our use case

### Negative
- Additional operational complexity vs managed options
- Team needs PostgreSQL training

### Neutral
- Need to set up backups and monitoring
```

## Writing Guidelines

### Prefer natural section headings

- Avoid headings like **"Executive Summary"** (reads AI-generated). Prefer **"TL;DR"** or **"Summary"**.

### Be Concise

```markdown
❌ In order to be able to run the application...
✅ To run the application...

❌ It is important to note that the configuration...
✅ The configuration...
```

### Use Active Voice

```markdown
❌ The file is created by the script.
✅ The script creates the file.

❌ An error will be returned if validation fails.
✅ The function returns an error if validation fails.
```

### Use Present Tense

```markdown
❌ The function will return a list of users.
✅ The function returns a list of users.

❌ This command installed the package.
✅ This command installs the package.
```

### Include Examples

```markdown
❌ Use the `fetch` function to make requests.

✅ Use the `fetch` function to make requests:

```javascript
const response = await fetch('/api/users');
const users = await response.json();
```

```

## Code Documentation

### Function Documentation
```python
def calculate_discount(price: float, percentage: float) -> float:
    """
    Calculate discounted price.
    
    Args:
        price: Original price in dollars.
        percentage: Discount percentage (0-100).
    
    Returns:
        Discounted price.
    
    Raises:
        ValueError: If percentage is not between 0 and 100.
    
    Example:
        >>> calculate_discount(100, 20)
        80.0
    """
    if not 0 <= percentage <= 100:
        raise ValueError("Percentage must be between 0 and 100")
    return price * (1 - percentage / 100)
```

### API Documentation

```yaml
/users/{id}:
  get:
    summary: Get user by ID
    description: |
      Retrieves a single user by their unique identifier.
      Returns 404 if the user doesn't exist.
    parameters:
      - name: id
        in: path
        required: true
        description: The user's unique identifier
        schema:
          type: string
          format: uuid
    responses:
      200:
        description: User found
      404:
        description: User not found
```

## Changelog Format

```markdown
# Changelog

## [1.2.0] - 2024-01-15

### Added
- New feature X

### Changed
- Updated dependency Y

### Fixed
- Bug in function Z

### Deprecated
- Old API endpoint

### Removed
- Legacy support for A

### Security
- Fixed vulnerability CVE-XXXX
```
