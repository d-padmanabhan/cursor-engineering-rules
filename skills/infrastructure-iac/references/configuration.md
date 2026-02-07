# Configuration Management

## Configuration Precedence

Configuration is applied in order, with later sources overriding earlier ones:

1. **System configuration** (`/etc/gitconfig`, `/etc/app/config.yaml`)
2. **User configuration** (`~/.gitconfig`, `~/.app/config.yaml`)
3. **Local/project configuration** (`.git/config`, `./config.yaml`)
4. **Environment variables** (`GIT_AUTHOR_NAME=...`, `APP_API_KEY=...`)
5. **Command-line parameters** (`git commit --author=...`, `app --api-key=...`)

This pattern is used by Git, SSH, and many Unix tools. Use this hierarchy to allow:

- System defaults
- User preferences
- Project settings
- Runtime environment overrides
- Explicit command-line overrides

### Precedence Examples

**Git Configuration:**

```bash
# System-wide (lowest priority)
/etc/gitconfig

# User-specific
~/.gitconfig

# Repository-specific (highest priority)
.git/config

# Environment variable override
GIT_AUTHOR_NAME="John Doe" git commit

# Command-line override (highest)
git commit --author="Jane Doe"
```

**SSH Configuration:**

```bash
# System-wide
/etc/ssh/ssh_config

# User-specific
~/.ssh/config

# Command-line override
ssh -p 2222 user@host
```

**Application Configuration:**

```python
# Load in precedence order
config = {}
config.update(load_system_config())      # 1. System
config.update(load_user_config())        # 2. User
config.update(load_project_config())     # 3. Project
config.update(load_env_vars())           # 4. Environment
config.update(parse_cli_args())          # 5. Command-line
```

## 12-Factor App Principles

1. **Codebase**: One codebase, many deploys
2. **Dependencies**: Explicitly declare and isolate
3. **Config**: Store in environment
4. **Backing services**: Treat as attached resources
5. **Build, release, run**: Strictly separate stages
6. **Processes**: Stateless, share-nothing
7. **Port binding**: Export via port binding
8. **Concurrency**: Scale out via processes
9. **Disposability**: Fast startup, graceful shutdown
10. **Dev/prod parity**: Keep environments similar
11. **Logs**: Treat as event streams
12. **Admin processes**: Run as one-off processes

## Environment Variables

### String Type

Environment variables are **strings** in the OS. Convert them in your application:

```python
# GOOD: Explicit conversion
port = int(os.getenv("PORT", "8080"))
timeout = float(os.getenv("TIMEOUT", "30.0"))
debug = os.getenv("DEBUG") == "1"

# BAD: Assuming type
port = os.getenv("PORT", 8080)  # Wrong! Default should be string
```

### Boolean Values

**Use `1` for true. Anything that is not `1` is false.**

```python
# GOOD: Consistent boolean handling
debug = os.getenv("DEBUG") == "1"
verbose = os.getenv("VERBOSE") == "1"
enabled = os.getenv("FEATURE_ENABLED") == "1"

# BAD: Parsing various strings
debug = os.getenv("DEBUG", "false").lower() in ["true", "1", "yes", "on"]
# This is brittle and opinionated
```

**Rationale:**

- Simple and unambiguous
- Works across all languages
- No parsing ambiguity
- Consistent with Unix conventions

### Required Values

**Fail fast if required configuration is missing:**

```python
# GOOD: Fail fast with clear error
api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError(
        "API_KEY environment variable is required. "
        "Set it with: export API_KEY=your-key"
    )

# BAD: Silent failure or default
api_key = os.getenv("API_KEY", "")  # What if empty string?
# Later: api_key is empty, fails mysteriously
```

### Default Values

Provide sensible defaults when appropriate:

```python
# GOOD: Sensible defaults
port = int(os.getenv("PORT", "8080"))
log_level = os.getenv("LOG_LEVEL", "INFO")
timeout = int(os.getenv("TIMEOUT", "30"))

# GOOD: No default for required values
api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError("API_KEY is required")
```

### Bash Examples

```bash
# Load from .env file
export $(grep -v '^#' .env | xargs)

# Required variables with defaults
DATABASE_URL="${DATABASE_URL:?DATABASE_URL is required}"
LOG_LEVEL="${LOG_LEVEL:-INFO}"
PORT="${PORT:-8080}"
```

## Configuration Files

### YAML Configuration

```yaml
# config.yaml
server:
  host: 0.0.0.0
  port: 8080
  
database:
  host: ${DB_HOST:-localhost}
  port: ${DB_PORT:-5432}
  name: ${DB_NAME:-myapp}
  
logging:
  level: ${LOG_LEVEL:-INFO}
  format: json
```

### Environment-Specific Overrides

```
config/
├── default.yaml      # Base config
├── development.yaml  # Dev overrides
├── staging.yaml      # Staging overrides
└── production.yaml   # Prod overrides
```

## Secret Management

**Never hardcode secrets** in code or configuration files. Use secret managers.

### AWS Secrets Manager

**Python Example:**

```python
import boto3
from botocore.exceptions import ClientError

def get_secret(secret_name: str, region_name: str = "us-east-1") -> str:
    """Retrieve secret from AWS Secrets Manager."""
    client = boto3.client("secretsmanager", region_name=region_name)
    
    try:
        response = client.get_secret_value(SecretId=secret_name)
        return response["SecretString"]
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            raise ValueError(f"Secret {secret_name} not found")
        raise

# Usage
db_password = get_secret("myapp/database/password")
```

**Terraform Example:**

```hcl
resource "aws_secretsmanager_secret" "db_password" {
  name = "myapp/db_password"
}

data "aws_secretsmanager_secret_version" "db_password" {
  secret_id = aws_secretsmanager_secret.db_password.id
}

# Use in application
output "db_password" {
  value = data.aws_secretsmanager_secret_version.db_password.secret_string
  sensitive = true
}
```

### HashiCorp Vault

**Python Example:**

```python
import hvac

def get_vault_secret(path: str) -> dict:
    """Retrieve secret from HashiCorp Vault."""
    client = hvac.Client(
        url=os.getenv("VAULT_ADDR"),
        token=os.getenv("VAULT_TOKEN")
    )
    
    try:
        response = client.secrets.kv.v2.read_secret_version(path=path)
        return response["data"]["data"]
    except Exception as e:
        raise ValueError(f"Failed to retrieve secret from Vault: {e}")

# Usage
secrets = get_vault_secret("secret/data/myapp/prod")
db_password = secrets["password"]
```

**CLI Example:**

```bash
# Store secret
vault kv put secret/myapp db_password=supersecret

# Read secret
vault kv get -field=db_password secret/myapp

# Use in application
export DB_PASSWORD=$(vault kv get -field=db_password secret/myapp)
```

### Kubernetes Secrets

**Create Secret:**

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
type: Opaque
stringData:
  username: admin
  password: ${DB_PASSWORD}  # From CI/CD pipeline
```

**Use in Pod:**

```yaml
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: app
    env:
    - name: DB_USERNAME
      valueFrom:
        secretKeyRef:
          name: db-credentials
          key: username
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: db-credentials
          key: password
```

**Python Example (Reading from K8s):**

```python
from kubernetes import client, config

def get_k8s_secret(namespace: str, secret_name: str, key: str) -> str:
    """Retrieve secret from Kubernetes."""
    config.load_incluster_config()  # In-cluster
    # Or: config.load_kube_config()  # Local development
    
    v1 = client.CoreV1Api()
    secret = v1.read_namespaced_secret(secret_name, namespace)
    return base64.b64decode(secret.data[key]).decode("utf-8")
```

### Azure Key Vault

**Python Example:**

```python
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

def get_azure_secret(vault_url: str, secret_name: str) -> str:
    """Retrieve secret from Azure Key Vault."""
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=vault_url, credential=credential)
    
    try:
        secret = client.get_secret(secret_name)
        return secret.value
    except Exception as e:
        raise ValueError(f"Failed to retrieve secret: {e}")

# Usage
db_password = get_azure_secret(
    vault_url="https://myvault.vault.azure.net/",
    secret_name="db-password"
)
```

### Google Secret Manager

**Python Example:**

```python
from google.cloud import secretmanager

def get_gcp_secret(project_id: str, secret_id: str, version: str = "latest") -> str:
    """Retrieve secret from Google Secret Manager."""
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version}"
    
    try:
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        raise ValueError(f"Failed to retrieve secret: {e}")

# Usage
db_password = get_gcp_secret("my-project", "db-password")
```

### Secret Management Best Practices

1. **Never commit secrets** to version control
2. **Use secret managers** for production environments
3. **Rotate secrets regularly** (every 90 days recommended)
4. **Use least privilege** - only grant access to what's needed
5. **Audit secret access** - log who accessed what and when
6. **Use different secrets** for different environments
7. **Validate secret format** - ensure secrets meet requirements
8. **Handle secret retrieval failures** gracefully
9. **Cache secrets** appropriately (don't fetch on every request)
10. **Use environment variables** for local development only

## Feature Flags

```python
# Simple feature flags
FEATURES = {
    "new_dashboard": os.getenv("FEATURE_NEW_DASHBOARD", "false").lower() == "true",
    "beta_api": os.getenv("FEATURE_BETA_API", "false").lower() == "true",
}

if FEATURES["new_dashboard"]:
    enable_new_dashboard()
```

## Configuration Validation

**Validate Early:** Check configuration at startup, not during runtime.

### Python with Pydantic

```python
from pydantic import BaseModel, Field, validator
from typing import Optional

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
    api_key: str  # Required, no default

    @validator("api_key")
    def validate_api_key(cls, v):
        if not v or len(v) < 32:
            raise ValueError("api_key must be at least 32 characters")
        return v

# Load and validate
config = AppConfig(
    server={"host": os.getenv("HOST", "localhost")},
    api_key=os.getenv("API_KEY")  # Will raise if missing
)
```

### Go Example

```go
package config

import (
    "os"
    "strconv"
    "fmt"
)

type Config struct {
    APIKey string
    APIURL string
    Timeout int
    Debug bool
}

func LoadFromEnv() (*Config, error) {
    apiKey := os.Getenv("API_KEY")
    if apiKey == "" {
        return nil, fmt.Errorf("API_KEY environment variable required")
    }

    timeout := 30
    if timeoutStr := os.Getenv("TIMEOUT"); timeoutStr != "" {
        var err error
        timeout, err = strconv.Atoi(timeoutStr)
        if err != nil {
            return nil, fmt.Errorf("invalid TIMEOUT: %w", err)
        }
    }

    return &Config{
        APIKey: apiKey,
        APIURL: getEnvOrDefault("API_URL", "https://api.acme.com"),
        Timeout: timeout,
        Debug: os.Getenv("DEBUG") == "1",
    }, nil
}

func getEnvOrDefault(key, defaultValue string) string {
    if value := os.Getenv(key); value != "" {
        return value
    }
    return defaultValue
}
```

### Early Validation Pattern

```python
# GOOD: Validate at startup
def load_config():
    config = AppConfig.from_env()  # Raises if invalid
    return config

# BAD: Validate during runtime
def process_request():
    api_key = os.getenv("API_KEY")  # May be None!
    # ... later in code ...
    if not api_key:  # Too late!
        raise ValueError("API_KEY required")
```

## Best Practices

1. **Never commit secrets** to version control
2. **Use environment variables** for configuration that varies by environment
3. **Validate configuration** at startup
4. **Fail fast** if required configuration is missing
5. **Document** all configuration options
6. **Use defaults** for optional settings
7. **Separate secrets** from other configuration
8. **Rotate secrets** regularly
9. **Audit access** to sensitive configuration
10. **Version** configuration changes
