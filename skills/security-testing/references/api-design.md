# API Design

## REST Best Practices

### Resource Naming

```
GET    /users           # List users
POST   /users           # Create user
GET    /users/{id}      # Get user
PUT    /users/{id}      # Replace user
PATCH  /users/{id}      # Partial update
DELETE /users/{id}      # Delete user

# Nested resources
GET    /users/{id}/orders
POST   /users/{id}/orders
```

### HTTP Status Codes

| Code | Meaning | Use When |
|------|---------|----------|
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid input |
| 401 | Unauthorized | Missing auth |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Duplicate, conflict |
| 422 | Unprocessable | Validation error |
| 429 | Too Many Requests | Rate limit |
| 500 | Server Error | Internal error |

### Response Format

```json
{
  "data": {
    "id": "123",
    "name": "Alice",
    "email": "alice@acme.com"
  }
}

// Error response
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid email format",
    "details": [
      {"field": "email", "message": "Must be valid email"}
    ]
  }
}
```

## Versioning

```
# URL path (recommended)
GET /v1/users
GET /v2/users

# Header
Accept: application/vnd.acme.v1+json

# Query parameter
GET /users?version=1
```

## Pagination

```json
GET /users?page=2&limit=20

{
  "data": [...],
  "pagination": {
    "page": 2,
    "limit": 20,
    "total": 100,
    "total_pages": 5,
    "next": "/users?page=3&limit=20",
    "prev": "/users?page=1&limit=20"
  }
}
```

## Filtering and Sorting

```
# Filtering
GET /users?status=active&role=admin

# Sorting
GET /users?sort=name        # Ascending
GET /users?sort=-created_at # Descending

# Field selection
GET /users?fields=id,name,email
```

## Authentication

```python
# JWT Bearer token
@app.before_request
def authenticate():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        g.user = User.get(payload["sub"])
    except jwt.InvalidTokenError:
        abort(401)
```

## Rate Limiting

```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per minute"]
)

@app.route("/api/search")
@limiter.limit("10 per minute")
def search():
    pass
```

## OpenAPI Documentation

```yaml
openapi: 3.0.3
info:
  title: User API
  version: 1.0.0

paths:
  /users:
    get:
      summary: List users
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
      responses:
        200:
          description: List of users
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/User'

components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        email:
          type: string
          format: email
```
