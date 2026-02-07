---
name: security-testing
description: Security best practices (OWASP Top 10) and testing strategies for software development. Covers secure coding, vulnerability prevention, testing pyramid, API design, and observability patterns. Use when reviewing code for security, writing tests, designing APIs, or when asking about security vulnerabilities, testing strategies, logging, or monitoring.
---

# Security & Testing

## Security Principles

1. **Defense in Depth**: Multiple layers of security
2. **Least Privilege**: Minimum necessary permissions
3. **Fail Secure**: Default to deny
4. **Zero Trust**: Never trust, always verify

## OWASP Top 10 Quick Reference

| # | Vulnerability | Prevention |
|---|---------------|------------|
| 1 | Broken Access Control | RBAC, deny by default, audit logs |
| 2 | Cryptographic Failures | TLS, strong algorithms, key management |
| 3 | Injection | Parameterized queries, input validation |
| 4 | Insecure Design | Threat modeling, secure patterns |
| 5 | Security Misconfiguration | Hardened defaults, minimal services |
| 6 | Vulnerable Components | Dependency scanning, updates |
| 7 | Auth/Identity Failures | MFA, session management |
| 8 | Software/Data Integrity | Signed artifacts, CI/CD security |
| 9 | Logging/Monitoring Failures | Centralized logs, alerting |
| 10 | SSRF | Input validation, allowlists |

## Security Checklist

- [ ] No hardcoded secrets
- [ ] Secrets not logged
- [ ] Input validation on all boundaries
- [ ] Parameterized queries
- [ ] Dependencies scanned for CVEs
- [ ] Authentication & authorization implemented
- [ ] HTTPS enforced
- [ ] Security headers configured
- [ ] Rate limiting in place
- [ ] Audit logging enabled

## Testing Pyramid

```
        /\
       /  \     E2E Tests (few)
      /----\
     /      \   Integration Tests
    /--------\
   /          \ Unit Tests (many)
  /------------\
```

| Type | Purpose | Speed | Coverage |
|------|---------|-------|----------|
| Unit | Test isolated logic | Fast | High |
| Integration | Test component interaction | Medium | Medium |
| E2E | Test full user flows | Slow | Low |

## Testing Best Practices

```python
# Arrange-Act-Assert pattern
def test_user_creation():
    # Arrange
    user_data = {"name": "Alice", "email": "alice@acme.com"}
    
    # Act
    user = create_user(user_data)
    
    # Assert
    assert user.name == "Alice"
    assert user.email == "alice@acme.com"

# Test edge cases
def test_empty_input():
    with pytest.raises(ValueError):
        create_user({})

def test_invalid_email():
    with pytest.raises(ValidationError):
        create_user({"name": "Bob", "email": "invalid"})
```

## API Security

```yaml
# Essential security headers
Content-Security-Policy: default-src 'self'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

```python
# Rate limiting
from flask_limiter import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.route("/api/login")
@limiter.limit("5 per minute")
def login():
    pass
```

## Observability

### Three Pillars

| Pillar | Purpose | Tools |
|--------|---------|-------|
| Logs | Event records | ELK, CloudWatch |
| Metrics | Numerical measurements | Prometheus, DataDog |
| Traces | Request flows | Jaeger, X-Ray |

### Structured Logging

```python
logger.info("User action", extra={
    "user_id": user.id,
    "action": "login",
    "ip": request.remote_addr,
    "timestamp": datetime.utcnow().isoformat()
})
```

## Detailed References

- **OWASP Security**: See [references/owasp-security.md](references/owasp-security.md)
- **Identity & Access**: See [references/identity-access.md](references/identity-access.md) for IAM, OIDC/PKCE, SAML/ADFS, PKI, PAM
- **Testing Strategies**: See [references/testing-strategies.md](references/testing-strategies.md)
- **API Design**: See [references/api-design.md](references/api-design.md)
- **Observability**: See [references/observability.md](references/observability.md)
