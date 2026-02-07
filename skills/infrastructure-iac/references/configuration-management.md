# Configuration Management Patterns

Manage configuration consistently across applications with clear precedence, proper validation, and secure defaults.

## Configuration Precedence (5-Level Hierarchy)

Configuration is applied in order, with later sources overriding earlier ones:

1. **System configuration** (`/etc/gitconfig`, `/etc/app/config.yaml`)
2. **User configuration** (`~/.gitconfig`, `~/.app/config.yaml`)
3. **Local/project configuration** (`.git/config`, `./config.yaml`)
4. **Environment variables** (`GIT_AUTHOR_NAME=...`, `APP_API_KEY=...`)
5. **Command-line parameters** (`git commit --author=...`, `app --api-key=...`)

This pattern is used by Git, SSH, and many Unix tools. Benefits:

- System defaults
- User preferences
- Project settings
- Runtime environment overrides
- Explicit command-line overrides

## Environment Variables

### String Type (Critical)

Environment variables are **strings** in the OS. Always convert explicitly:

```python
# ✅ GOOD: Explicit conversion
port = int(os.getenv("PORT", "8080"))
timeout = float(os.getenv("TIMEOUT", "30.0"))
debug = os.getenv("DEBUG") == "1"

# ❌ BAD: Assuming type
port = os.getenv("PORT", 8080)  # Wrong! Default should be string
```

### Boolean Values

**Use `1` for true. Anything else is false.**

```python
# ✅ GOOD: Consistent boolean handling
debug = os.getenv("DEBUG") == "1"
verbose = os.getenv("VERBOSE") == "1"
enabled = os.getenv("FEATURE_ENABLED") == "1"

# ❌ BAD: Parsing various strings (brittle)
debug = os.getenv("DEBUG", "false").lower() in ["true", "1", "yes", "on"]
```

**Rationale:** Simple, unambiguous, works across all languages, no parsing ambiguity.

### Required Values

**Fail fast if required configuration is missing:**

```python
# ✅ GOOD: Fail fast with clear error
api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError(
        "API_KEY environment variable is required. "
        "Set it with: export API_KEY=your-key"
    )

# ❌ BAD: Silent failure
api_key = os.getenv("API_KEY", "")  # Empty string = mysterious failures later
```

### Default Values

```python
# ✅ GOOD: Sensible defaults for optional config
port = int(os.getenv("PORT", "8080"))
log_level = os.getenv("LOG_LEVEL", "INFO")
timeout = int(os.getenv("TIMEOUT", "30"))

# ✅ GOOD: No default for required values
api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError("API_KEY is required")
```

## Configuration File Patterns

### Environment-Specific Configuration

```python
import os
import yaml

def load_config():
    env = os.getenv("ENVIRONMENT", "development")

    # Load base config
    with open("config/base.yaml") as f:
        config = yaml.safe_load(f)

    # Override with environment-specific config
    env_config_path = f"config/{env}.yaml"
    if os.path.exists(env_config_path):
        with open(env_config_path) as f:
            env_config = yaml.safe_load(f)
            config = merge_config(config, env_config)

    # Override with environment variables
    config = apply_env_overrides(config)

    return config
```

## Configuration Validation

### Validate Early (Pydantic Example)

```python
from pydantic import BaseModel, Field, validator

class ServerConfig(BaseModel):
    host: str = Field(default="localhost")
    port: int = Field(default=8080, ge=1, le=65535)
    timeout: int = Field(default=30, ge=1)

    @validator("host")
    def validate_host(cls, v):
        if not v:
            raise ValueError("host cannot be empty")
        return v

class AppConfig(BaseModel):
    server: ServerConfig
    api_key: str  # Required

    @validator("api_key")
    def validate_api_key(cls, v):
        if not v or len(v) < 32:
            raise ValueError("api_key must be at least 32 characters")
        return v

# Load and validate
config = AppConfig(
    server={"host": "0.0.0.0", "port": 8080},
    api_key=os.getenv("API_KEY")
)
```

## Secret Management

**Never commit secrets to version control:**

```bash
# ✅ GOOD: Use environment variables
export DATABASE_PASSWORD="secret"
export API_KEY="key"

# ✅ GOOD: Use secret management
aws secretsmanager get-secret-value --secret-id myapp/db-password
vault kv get secret/myapp/db-password

# ❌ BAD: Hardcoded secrets
db_password = "hardcoded_secret"  # Never do this
```

### .env File Pattern

```bash
# .env (gitignored)
DATABASE_URL=postgresql://user:pass@localhost/db
API_KEY=your-api-key
DEBUG=1
```

```python
# Load .env file
from dotenv import load_dotenv
load_dotenv()

# Access as environment variables
database_url = os.getenv("DATABASE_URL")
```

## Type Conversion Reference

| Type | Pattern | Example |
|------|---------|---------|
| **String** | Direct access | `os.getenv("NAME", "default")` |
| **Integer** | `int()` conversion | `int(os.getenv("PORT", "8080"))` |
| **Float** | `float()` conversion | `float(os.getenv("TIMEOUT", "30.0"))` |
| **Boolean** | Check for "1" | `os.getenv("DEBUG") == "1"` |
| **List** | Split string | `os.getenv("HOSTS", "").split(",")` |
| **JSON** | Parse JSON | `json.loads(os.getenv("CONFIG", "{}"))` |

## Best Practices

1. **Fail Fast**: Validate configuration at startup
2. **Document Defaults**: Comment why defaults are chosen
3. **Use Type Hints**: Make configuration schema explicit
4. **Validate Values**: Check ranges, formats, required fields
5. **Separate Secrets**: Keep secrets out of config files
6. **Environment-Specific**: Use different configs per environment
7. **Precedence Clear**: Document override order
8. **Test Configuration**: Include config validation in tests

## Security Checklist

- [ ] No secrets in version control
- [ ] Secrets loaded from environment or secret manager
- [ ] Configuration validated at startup
- [ ] Sensitive values redacted in logs
- [ ] Default values are secure (not debug mode, etc.)
- [ ] File permissions correct (600 for secrets)
- [ ] Configuration precedence documented
- [ ] Required values fail fast with clear errors

## Resources

See [infrastructure-iac/references/terraform-variables.md](terraform-variables.md) for Terraform-specific configuration patterns.
